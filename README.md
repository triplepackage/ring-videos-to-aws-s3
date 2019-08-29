# Ring Videos to AWS S3 and Dropbox
Python script to download Ring videos and copy them to AWS S3 and Dropbox 

Install pre-requisites
<pre>
sudo pip install --upgrade awscli
sudo pip install boto3
pip install ring_doorbell
</pre>

Run the script

<pre>
Johns-MacBook-Pro:ring-videos-to-aws-s3 admin$ python upload-dropbox.py 
2019/08/28/2019-08-28-19-16-25.mp4
2019/08/28/2019-08-28-19-13-48.mp4
2019/08/28/2019-08-28-16-36-19.mp4
2019/08/28/2019-08-28-16-24-38.mp4
2019/08/28/2019-08-28-16-21-56.mp4
2019/08/28/2019-08-28-15-50-48.mp4
2019/08/28/2019-08-28-14-35-39.mp4
2019/08/28/2019-08-28-13-01-15.mp4
2019/08/28/2019-08-28-12-38-40.mp4
2019/08/28/2019-08-28-12-33-46.mp4
2019/08/28/2019-08-28-06-18-13.mp4
2019/08/28/2019-08-28-06-09-13.mp4
2019/08/28/2019-08-28-05-55-54.mp4
</pre>

![Alt text](./images/images-003.jpg?raw=true "Ring Camera")
![Alt text](./images/images-002.jpg?raw=true "AWS S3")
![Alt text](./images/images-004.jpg?raw=true "Dropbox")
