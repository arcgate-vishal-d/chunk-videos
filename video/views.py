import os
import time

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.response import Response
from rest_framework import status

from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from moviepy.editor import VideoFileClip
from moviepy.video.io.VideoFileClip import VideoFileClip

from .models import Video
from .serializers import VideoSerializer

class VideoUploadView(APIView):
    def post(self, request):
        media_file = request.data['file']
        allowed_Extentions = ['mp4', 'avi', 'mov', 'jpg', 'jpeg','txt','png','svg','pdf']
        file_extention = media_file.content_type.lower().split('/')
        if file_extention[1] not in allowed_Extentions:
            return Response({"msg": "Invalid File Formate."}, status=status.HTTP_204_NO_CONTENT)

        if media_file.content_type.startswith('video'):
            return self.process_video(media_file, file_extention[1])
        elif media_file.content_type.startswith('image'):
            return self.process_image(media_file, file_extention[1])
        else:
            return Response({'message': 'Invalid file format. Please upload a video or an image file.'}, status=400)

    def process_video(self, video_file, file_extention):
        try:
            with VideoFileClip(video_file.temporary_file_path()) as video_clip:
                video_duration = video_clip.duration
        except Exception as e:
            print(f"Error getting video duration: {str(e)}")
            video_duration = None

        if video_duration is not None:
            chunk_duration_seconds = 90  
            video_name = os.path.splitext(video_file.name)[0]

            output_folder = f'media/videos/{video_name}/'
            os.makedirs(output_folder, exist_ok=True)

            start_time = 0
            chunk_number = 1
            while start_time < video_duration:
                end_time = min(start_time + chunk_duration_seconds, video_duration)
                timestamp = int(time.time())
                output_file = f'chunk_{chunk_number}_{timestamp}.{file_extention}'

                Video.objects.create(
                    file=os.path.join(output_folder, output_file),
                )

                ffmpeg_extract_subclip(video_file.temporary_file_path(), start_time, end_time, targetname=os.path.join(output_folder, output_file))
                start_time = end_time
                chunk_number += 1

            return Response({'message': 'Video file chunked successfully'})

    def process_image(self, image_file, file_extention):
        image_name = os.path.splitext(image_file.name)[0]
        output_folder = f'media/images/{image_name}/'
        os.makedirs(output_folder, exist_ok=True)

        timestamp = int(time.time())  
        output_file = f'{image_name}_{timestamp}.{file_extention}'

        Video.objects.create(
            file=os.path.join(output_folder, output_file),
        )

        with open(os.path.join(output_folder, output_file), 'wb') as destination:
            for chunk in image_file.chunks():
                destination.write(chunk)

        return Response({'message': 'Image file processed successfully'})


class DashboardView(APIView):

    def get(self, request):
        videos = Video.objects.all()
        serializer = VideoSerializer(videos, many=True)
        response_data = {
            "video": serializer.data,
        }
        return Response(response_data, status=status.HTTP_200_OK)
    