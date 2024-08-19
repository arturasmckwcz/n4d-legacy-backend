import json

import structlog
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from parse_opportunities.utils import parse_opportunity_json

logger = structlog.get_logger(__name__)


class OpportunitiesJSONFileUploadView(APIView):
    permission_classes = (AllowAny,)
    parser_classes = [MultiPartParser]

    def post(self, request, format=None):
        json_file = request.FILES["json_file"]
        file_name = str(json_file)

        try:
            json_data = json.load(json_file)
        except json.JSONDecodeError:
            logger.error(f"Invalid content of file: {file_name}")
            return Response({"message": "ERROR: Invalid JSON file"}, status=400)

        logger.info(f"File {file_name} successfully loaded")

        count = parse_opportunity_json(json_data) if isinstance(json_data, list) else 0

        return Response(
            {"message": f"JSON file uploaded and successfully processed {count} items"}
        )
