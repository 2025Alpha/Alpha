from django.core.exceptions import ValidationError
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Travel
from .serializers import TravelSerializer
from config.settings import SEOUL_PUBLIC_DATA_SERVICE_KEY
from .serializers import EventSerializer
from .modules.tour_api import NearEventInfo

from .models import Event

class TravelViewSet(viewsets.ModelViewSet):
    queryset = Travel.objects.all()
    serializer_class = TravelSerializer
    permission_classes = [IsAuthenticated] # 로그인한 사용자만 api를 승인합니다.

    def create(self, request, *args, **kwargs):  # 새로운 여행 등록 API
        user_sub = request.user.sub  # 액세스 토큰에서 sub 값 가져오기

        # request.data를 변경 가능한 딕셔너리로 변환 후 user 추가
        travel_data = dict(request.data).copy()
        travel_data["user"] = user_sub

        serializer = self.get_serializer(data=travel_data)  # 수정된 데이터로 serializer 초기화

        if serializer.is_valid():  # 데이터에 모든 필드가 다 있을 때 실행되는 조건문
            travel = serializer.save()  # ORM을 이용해 저장

            # json 응답을 반환
            return Response({
                "tour_id": travel.id,
                "tour_name": travel.tour_name,
                "start_date": str(travel.start_date),
                "end_date": str(travel.end_date)
            }, status=status.HTTP_201_CREATED)

        # 데이터가 일부 누락되었을 때
        return Response({
            "error": "400",
            "message": "필수 파라미터 중 일부 혹은 전체가 없습니다. 필수 파라미터 목록을 확인해주세요"
        }, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request, *args, **kwargs):  # 리스트 조회 API
        user_sub = request.user.sub  # 액세스 토큰에서 sub 값 가져오기
        queryset = self.get_queryset().filter(user_id=user_sub)  # 로그인한 사용자의 여행만 조회
        serializer = self.get_serializer(queryset, many=True)

        # json 응답을 반환
        response_data = [
            {
                "tour_id": travel["id"],
                "tour_name": travel["tour_name"],
                "start_date": travel["start_date"],
                "end_date": travel["end_date"]
            } for travel in serializer.data
        ]

        return Response(response_data, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):  # 내 여행 가져오기(하나만) API
        user_sub = request.user.sub  # 액세스 토큰에서 sub 값 가져오기
        tour_id = kwargs.get('pk')

        try:
            travel = Travel.objects.get(id=tour_id, user_id=user_sub)  # 로그인한 사용자의 여행인지 확인
        except Travel.DoesNotExist:
            return Response({
                "error": "404",
                "message": "해당 여행 ID가 존재하지 않거나, 접근 권한이 없습니다."
            }, status=status.HTTP_404_NOT_FOUND)

        return Response({
            "tour_id": travel.id,
            "tour_name": travel.tour_name,
            "start_date": str(travel.start_date),
            "end_date": str(travel.end_date)
        }, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):  # 여행 정보 수정 API
        user_sub = request.user.sub  # 액세스 토큰에서 sub 값 가져오기
        tour_id = kwargs.get('pk')

        try:
            travel = Travel.objects.get(id=tour_id, user_id=user_sub)  # 로그인한 사용자의 여행인지 확인
        except Travel.DoesNotExist:
            return Response({
                "error": "404",
                "message": "해당 여행 ID가 존재하지 않거나, 접근 권한이 없습니다."
            }, status=status.HTTP_404_NOT_FOUND)

        data = request.data  # 수정할 데이터 가져오기

        if "tour_name" in data:
            travel.tour_name = data["tour_name"]
        if "start_date" in data:
            travel.start_date = data["start_date"]
        if "end_date" in data:
            travel.end_date = data["end_date"]

        travel.save()  # 변경 사항 저장

        return Response({
            "tour_id": travel.id,
            "tour_name": travel.tour_name,
            "start_date": str(travel.start_date),
            "end_date": str(travel.end_date)
        }, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):  # 여행 삭제 API
        user_sub = request.user.sub  # 액세스 토큰에서 sub 값 가져오기
        tour_id = kwargs.get('pk')

        try:
            travel = Travel.objects.get(id=tour_id, user_id=user_sub)  # 로그인한 사용자의 여행인지 확인
        except Travel.DoesNotExist:
            return Response({
                "error": "404",
                "message": "해당 여행 ID가 존재하지 않거나, 접근 권한이 없습니다."
            }, status=status.HTTP_404_NOT_FOUND)

        travel.delete()  # 여행 데이터 삭제
        return Response(status=status.HTTP_204_NO_CONTENT)  # 204 No Content 응답 반환
      
class NearEventView(viewsets.ModelViewSet):
    serializer_class =  EventSerializer# 이벤트 시리얼라이저 GET
    queryset = Event.objects.all() # 이벤트 모델 GET

    def list(self, request, *args, **kwargs):
        """
        해당 함수는 tour_api의 NearEventInfo 클래스를 통해 얻어온 주변 정보를 바탕으로 주변 문화 정보를 반환해줍니다.
        """
        mapX = request.GET.get('mapX', None)
        mapY = request.GET.get('mapY', None)
        radius = request.GET.get('radius', '0.5') # 반경 정보를 가져옵니다. default: 0.5km
        start_date = request.GET.get('start_date', None)
        end_date = request.GET.get('end_date', None)

        if mapX is None or mapY is None: # 필수 파라미터 검증
            return Response({"ERROR": "필수 파라미터 중 일부 혹은 전체가 없습니다."}, status=status.HTTP_400_BAD_REQUEST)

        if Event.objects.count() == 0: # 주변 행사 정보가 DB에 없을 경우, 코드는 200 OK로 보냅니다.
            return Response({"Message": "주변 행사 정보 데이터가 서버 내에 없습니다."}, status=status.HTTP_200_OK)

        event_info = NearEventInfo(Event, SEOUL_PUBLIC_DATA_SERVICE_KEY, Event.objects.all())
        try:
            events = event_info.get_near_by_events(float(mapY), float(mapX), float(radius)) # 주변 행사 정보를 불러옵니다.
        except ValueError:
            return Response({"ERROR": "경도, 위도, 반경 정보 일부 혹은 모두가 데이터 형식이 실수형이 아닙니다."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            if start_date is not None:
                events = events.filter(start_date__gte=start_date) # 시작 날짜보다 더 크거나 같은 데이터를 불러옵니다.
            if end_date is not None:
                events = events.filter(end_date__lte=end_date) # 마지막 날짜보다 더 작거나 같은 데이터를 불러옵니다.
        except ValidationError:
            return Response({"ERROR": "날짜 값이 날짜 형식이 아닙니다. 반드시 YYYY-MM-DD 형식이어야 합니다."}, status=status.HTTP_400_BAD_REQUEST)

        events = events.order_by('start_date') # 날짜 순 정렬

        serializer = self.get_serializer(events, many=True) # 시리얼라이저에 정보를 넣어 시리얼라이징합니다.
        return Response(serializer.data, status=status.HTTP_200_OK)

