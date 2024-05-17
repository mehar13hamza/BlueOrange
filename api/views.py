import csv
import difflib
import logging
from django.conf import settings
from rest_framework import generics
from rest_framework.response import Response
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework import status
import requests

logger = logging.getLogger(__name__)

zip_codes_data = []

def load_zip_codes():
    global zip_codes_data
    with open(settings.BASE_DIR / 'zips.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile, fieldnames=['zipcode', 'city',\
            'state', 'state_code', 'country', 'latitude', 'longitude'])
        zip_codes_data = [row for row in reader]

load_zip_codes()

class ZipCodeDetailView(APIView):
    """
    API View to retrieve details of a zip code.

    This endpoint retrieves the details of a given zip code. The zip code is passed
    as a parameter in the URL.

    Request Parameters:
    - zipcode: The zip code for which details are to be retrieved.

    Response Fields:
    - zipcode: The zip code.
    - city: The city associated with the zip code.
    - state: The state associated with the zip code.
    - state_code: The state code.
    - country: The country associated with the zip code.
    - latitude: The latitude coordinate of the zip code location.
    - longitude: The longitude coordinate of the zip code location.

    Methods:
    -------
    get(request, *args, **kwargs)
        Handles GET requests to retrieve details of the specified zip code.
    """
    permission_classes = [IsAuthenticated]
    lookup_field = 'zipcode'

    @swagger_auto_schema(
        operation_description="Retrieve details of a zip code.",
        responses={
            200: openapi.Response('Successful retrieval',\
                schema=openapi.Schema(type=openapi.TYPE_OBJECT)),
            404: openapi.Response('Zip code not found',\
                schema=openapi.Schema(type=openapi.TYPE_OBJECT)),
        }
    )
    def get(self, request, *args, **kwargs):
        zipcode = self.kwargs.get(self.lookup_field)
        zip_code_data = next((item for item in zip_codes_data if zipcode in item.values()), None)
        if zip_code_data:
            logger.info({
                'message': 'Zip code details retrieved successfully.',
            })
            return Response(zip_code_data)
        else:
            return Response({'message': 'Zip code not found.'}, status=status.HTTP_404_NOT_FOUND)


class TopZipCodesView(generics.GenericAPIView):
    """
    API View to retrieve the top zip codes for a given city name.

    This endpoint retrieves the top three zip codes that most closely match the given
    city name. The city name is provided in the request body.

    Request Body:
    - city_name: (string) The name of the city for which to find matching zip codes.
    - Example: {"city_name": "Holtsville"}

    Response Fields:
    - zipcode: The zip code.
    - city: The city associated with the zip code.
    - state: The state associated with the zip code.
    - state_code: The state code.
    - country: The country associated with the zip code.
    - latitude: The latitude coordinate of the zip code location.
    - longitude: The longitude coordinate of the zip code location.

    Methods:
    -------
    post(request)
        Handles POST requests to retrieve the top three zip codes matching the given city name.
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'city_name': openapi.Schema(type=openapi.TYPE_STRING,\
                    description='City name'),
            },
            required=['city_name']
        )
    )
    def post(self, request):
        city_name = request.data.get('city_name', '')
        queryset = []

        scores = [(zipcode, difflib.SequenceMatcher(None, city_name.lower(),\
            (zipcode.get('city') or '').lower()).ratio()) for zipcode in zip_codes_data]
        scores.sort(key=lambda x: x[1], reverse=True)

        top_zipcodes = scores[:3]

        queryset = [zipcode[0] for zipcode in top_zipcodes]

        logger.info({
            'message': 'Top zip codes retrieved successfully.',
        })
        return Response(queryset)

    
class OktaAPIView(APIView):
    """
    API View to handle authorization code exchange with Okta.

    This endpoint exchanges an authorization code for an access token from Okta.
    
    Request Parameters:
    - grant_type: "authorization_code"
    - code: Authorization code from Okta
    - redirect_uri: Redirect URI registered with Okta
    - client_id: Okta client ID
    - client_secret: Okta client secret

    Response Fields:
    - token_type: Type of token (e.g., "Bearer")
    - expires_in: Token validity duration in seconds
    - access_token: Access token for authentication
    - scope: Scopes granted by the access token
    - id_token: ID token with user information

    Methods:
    -------
    get(request)
        Handles GET requests to exchange the authorization code for an access token.
    """
    def get(self, request):
        code = request.query_params.get("code")
        if not code:
            return Response({"error": "Authorization code is missing"}, status=400)
        url = settings.OIDC_OP_TOKEN_ENDPOINT
        payload = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": settings.REDIRECT_URL,
            "client_id": settings.OIDC_RP_CLIENT_ID,
            "client_secret": settings.OIDC_RP_CLIENT_SECRET,
        }
        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
        }
        try:
            response = requests.post(url, headers=headers, data=payload)
            response.raise_for_status()  # Raise an exception for HTTP errors
            json_data = response.json()
        except requests.RequestException as e:
            return Response({"error": str(e)}, status=500)
        return Response(json_data)
