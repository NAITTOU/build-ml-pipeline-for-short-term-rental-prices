#!/usr/bin/env python
"""
Download from W&B the raw dataset and apply some basic data cleaning, exporting the result to a new artifact
"""
import argparse
import logging
import wandb
import pandas as pd


logging.basicConfig(level=logging.INFO, format="%(asctime)-15s %(message)s")
logger = logging.getLogger()


def go(args):

    run = wandb.init(job_type="basic_cleaning")
    run.config.update(args)

    # Download input artifact. This will also log that this script is using this
    # particular version of the artifact

    logger.info("Downloading artifact")
    artifact_local_path = run.use_artifact(args.input_artifact).file()
    df = pd.read_csv(artifact_local_path)

    # drop outliers
    logger.info("Dropping outliers")
    min_price = args.min_price
    max_price = args.max_price
    idx = df['price'].between(min_price, max_price)
    df = df[idx].copy()

    logger.info("Converting last_review column to Date")
    # Convert last_review to datetime
    df['last_review'] = pd.to_datetime(df['last_review'])
    
    logger.info("Saving Dataframe into disk")
    # save dataframe to disk
    df.to_csv("clean_sample.csv", index=False)

    # log artifact to wandb
    artifact = wandb.Artifact(
     name=args.output_artifact,
     type=args.output_type,
     description=args.output_description,
    )

    artifact.add_file("clean_sample.csv")

    logger.info("Logging artifact")
    run.log_artifact(artifact)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="A very basic data cleaning")


    parser.add_argument(
        "--input_artifact", 
        type=str,
        help="Fully-qualitied name for the artifact to be used as raw dataset",
        required=True
    )

    parser.add_argument(
        "--output_artifact", 
        type=str,
        help="Name for the W&B artifact that will be created",
        required=True
    )

    parser.add_argument(
        "--output_type", 
        type=str,
        help="Type of the artifact to create",
        required=True
    )

    parser.add_argument(
        "--output_description", 
        type=str,
        help="Description for the artifact",
        required=True
    )

    parser.add_argument(
        "--min_price", 
        type=float,
        help="the minimum price to consider",
        required=True
    )

    parser.add_argument(
        "--max_price", 
        type=float,
        help="the maximum price to consider",
        required=True
    )


    args = parser.parse_args()

    go(args)
