"""Main module."""

import logging
import os
from types import MethodType

import av
import boto3
import click
from smart_open import open

from video_processing import rgb_to_grayscale

logging.basicConfig(level=logging.INFO)


@click.command()
@click.option("--s3_input_path", type=str)
@click.option("--s3_output_path", type=str)
def main(
    s3_input_path: str,
    s3_output_path: str,
) -> None:
    """
    Process a video from an S3 input path, converts the video frames to grayscale, and
    writes the result to an S3 output path in MP4 format.

    Args:
        s3_input_path (str): The S3 path to the input video file.
        s3_output_path (str): The S3 path to the output video file.
    """
    logging.info(f"Params:\ns3_input_path: {s3_input_path}\ns3_output_path: {s3_output_path}\n")

    logging.info("Create boto3 session...")
    session = boto3.Session()
    s3_client = session.client(service_name="s3", region_name=os.environ["REGION_NAME"])

    with (
        open(
            s3_output_path,
            "wb",
            transport_params={"client": s3_client},
        ) as output_video,
        open(
            s3_input_path,
            "rb",
            transport_params={"client": s3_client},
        ) as input_video,
    ):
        # s3 writer isn't seekable in fact
        output_video.seekable = MethodType(lambda self: False, output_video)
        with (
            av.open(input_video, mode="r") as input_container,
            av.open(
                output_video,
                mode="w",
                format="mp4",
                options={"movflags": "frag_keyframe+empty_moov"},
            ) as output_container,
        ):
            logging.info("Get input streams...")
            input_video_stream = input_container.streams.video[0]
            input_audio_stream = input_container.streams.audio[0]

            logging.info("Create output streams...")
            output_video_stream = output_container.add_stream(
                codec_name=input_video_stream.codec_context.name,
                rate=input_video_stream.codec_context.rate,
            )
            # copy video params
            output_video_stream.width = input_video_stream.codec_context.width
            output_video_stream.height = input_video_stream.codec_context.height
            output_video_stream.pix_fmt = input_video_stream.codec_context.pix_fmt

            output_audio_stream = output_container.add_stream(
                codec_name=input_audio_stream.codec_context.name,
                rate=input_audio_stream.codec_context.rate,
            )

            logging.info("Start streaming...")
            for packet_index, input_packet in enumerate(input_container.demux()):
                logging.info(f"Process {packet_index} packet...")
                if input_packet.stream.type == "audio":
                    for input_audio_frame in input_packet.decode():
                        audio_packet = output_audio_stream.encode(input_audio_frame)
                        output_container.mux(audio_packet)
                elif input_packet.stream.type == "video":
                    for input_video_frame in input_packet.decode():
                        np_video_frame = input_video_frame.to_ndarray(format="rgb24")

                        # frame processing (convert to grayscale)
                        output_video_frame = av.VideoFrame.from_ndarray(
                            rgb_to_grayscale(np_video_frame), format="rgb24"
                        )

                        video_packet = output_video_stream.encode(output_video_frame)
                        output_container.mux(video_packet)

            logging.info("Flush encoders...")
            output_container.mux(output_video_stream.encode(None))
            output_container.mux(output_audio_stream.encode(None))


if __name__ == "__main__":
    main()
