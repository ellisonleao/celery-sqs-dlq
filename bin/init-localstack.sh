#!/bin/bash

set -e

awslocal sqs create-queue --queue-name test-queue.fifo --attributes FifoQueue=true
awslocal sqs create-queue --queue-name test-queue-dlq.fifo --attributes FifoQueue=true
awslocal sqs set-queue-attributes --queue-url http://sqs.us-east-1.localhost.localstack.cloud:4566/000000000000/test-queue.fifo --attributes '{"FifoQueue": "true", "VisibilityTimeout": "1", "RedrivePolicy": "{\"deadLetterTargetArn\":\"arn:aws:sqs:us-east-1:000000000000:test-queue-dlq.fifo\",\"maxReceiveCount\":\"1\"}"}'
