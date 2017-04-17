# Start with the dataquest python3 starter image.
FROM jupyter/minimal-notebook

LABEL maintainer "lambe.v@husky.neu.edu"

# Copy the Python script we want to run to the user home directory in the image.
COPY ./dataextraction1.py /home/ds/dataextraction1.py

# Create the data directory for the downloaded files.
#RUN mkdir -p /home/ds/data
RUN pip install BeautifulSoup4


# Set the working directory.
USER ds
WORKDIR /home/ds

# Run the script
ENTRYPOINT ["/opt/ds/bin/python3", "/home/ds/dataextraction1.py"]
