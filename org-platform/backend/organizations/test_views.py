"""
测试视图
"""

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny


class TestViewSet(viewsets.ViewSet):
    """测试API"""
    permission_classes = [AllowAny]

    @action(detail=False, methods=['get'])
    def test(self, request):
        """测试端点"""
        return Response({'message': '测试成功', 'status': 'ok'})
