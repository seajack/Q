"""
工作流相关URL配置
"""

from rest_framework.routers import DefaultRouter
from .workflow_views import WorkflowRuleViewSet, WorkflowRuleExecutionViewSet, WorkflowTemplateViewSet, SimpleWorkflowApiViewSet

router = DefaultRouter()
router.register(r'workflow-rules', WorkflowRuleViewSet)
router.register(r'workflow-executions', WorkflowRuleExecutionViewSet)
router.register(r'workflow-templates', WorkflowTemplateViewSet)
router.register(r'simple-workflow', SimpleWorkflowApiViewSet, basename='simple-workflow')

urlpatterns = router.urls
