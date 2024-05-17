# BlueOrange

## Zip Code Metadata API

This project provides a simple HTTP server that presents an API for retrieving metadata about zip codes. The server reads data from a provided CSV file and loads it into memory as an efficient data structure to support requests. The API supports two routes:

1. **Exact ZIP Code Lookup:** Takes an integer from the path representing an exact ZIP code and returns all fields for that zip code.
2. **Top Zip Codes by City Name:** Reads a field from the requested JSON POST body (a town/city name) and returns an array representing the top 3 zip codes whose town name most closely matches the query field. Each result includes a `score` field representing the closeness of the match, with the results sorted from closest to farthest match.

## Task Performed

- Created an HTTP server using Python and Django that presents an API for retrieving metadata about zip codes.
- Implemented two routes:
  1. Exact ZIP Code Lookup: Takes an integer from the path representing an exact ZIP code and returns all fields for that zip code.
  2. Top Zip Codes by City Name: Reads a field from the requested JSON POST body (a town/city name) and returns an array representing the top 3 zip codes whose town name most closely matches the query field. Each result includes a `score` field representing the closeness of the match, with the results sorted from closest to farthest match.
- Integrated Okta for authentication and authorization.
- Dockerize the application for easy deployment.
- Wrote comprehensive test cases covering the entire project, achieving a test case coverage report of 96%.
- Implemented API documentation using Swagger.


## Prerequisites
* Django Rest Framework application
* Okta Developer account
* A registered Okta application with proper configurations


### 1. Okta Application Setup:
* Log in to your Okta developer account.
* Navigate to Applications and click Add Application.
* Choose Web and set the sign-in redirect URI to http://localhost:8000/oidc/callback.
* Make a note of the Client ID and Client Secret from the application settings.

### Application Setup:

#### Configuration

Before running the application, ensure you have set up the following environment variables in your `.env` file:

- `OIDC_OP_TOKEN_ENDPOINT`: The token endpoint URL of the OpenID Connect (OIDC) provider.
- `OIDC_OP_USER_ENDPOINT`: The user endpoint URL of the OIDC provider.
- `OIDC_OP_AUTHORIZATION_ENDPOINT`: The authorization endpoint URL of the OIDC provider.
- `OIDC_RP_CLIENT_ID`: The client ID registered with the OIDC provider.
- `OIDC_RP_CLIENT_SECRET`: The client secret associated with the client ID.
- `OIDC_RP_SCOPES`: The OIDC scopes.
- `REDIRECT_URL`: The URL to which the OIDC provider should redirect after authentication.

These variables are used for configuring the OpenID Connect (OIDC) client for authentication in our application.

#### Docker

To build the Docker image for the BlueOrange project, use the following command:

```bash
docker build -t blue_orange .
```
To run the Docker container for the BlueOrange project, use the following command:
```bash
docker run -d -p 8000:8000 blue_orange
```

### Check Coverage Report
To run the coverage commands inside a Docker container, follow these steps:

 1. Access the Docker container shell: Use the following command to access the shell of your running Django container. Replace container_name with the name of your Django container.

```bash
docker exec -it container_name /bin/bash
```
 2. Run the coverage commands: Once inside the container, run the coverage commands as you would normally.

```bash
coverage run manage.py test
coverage report
```

### API Documentation

The API documentation for the BlueOrange project can be accessed using Swagger. To view the documentation, navigate to [http://localhost:8000/swagger/](http://localhost:8000/swagger/) in your web browser.

Swagger provides a user-friendly interface for exploring and testing the API endpoints. It also includes detailed descriptions of each endpoint and the expected request and response formats.


## Authentication Flow
### Initiate Authentication:
* Direct the user to the following Okta authorization endpoint from your frontend:
```
https://okta-domain/oauth2/default/v1/authorize?client_id=CLIENT_ID&response_type=code&scope=openid email profile&redirect_uri=http://localhost:8000/oidc/callback&state=StateValue
```
* Replace CLIENT_ID with your actual Okta application client ID.
* Replace state with your actual state value.
### User Authentication:
* The user will be prompted to enter their Okta credentials.
* After successful authentication and approval, Okta redirects to the specified redirect URI with an authorization code.
### Exchange Code for Token:
* The backend endpoint at http://localhost:8000/oidc/callback receives the authorization code.
* This code is then used to make a POST request to Okta’s token endpoint to exchange the code for tokens.
```
https://trial-4753028.okta.com/oauth2/default/v1/token
```
* The response from this endpoint includes the access tokens required for authenticating subsequent API requests.
```
{
    “token_type”: “Bearer”,
    “expires_in”: 3600,
    “access_token”: “ACCESS_TOKEN”,
    “scope”: “email profile openid”,
    “id_token”: “ID_TOKEN”
}
```

# Conclusion

In conclusion, the BlueOrange Zip Code Metadata API project provides a convenient and efficient way to retrieve metadata about zip codes. With routes for exact ZIP code lookup and top zip codes by city name, users can easily access relevant information.

The integration of Okta for authentication and authorization ensures secure access to the API. Additionally, the Dockerization of the application simplifies deployment, making it easier to manage and scale. The comprehensive test coverage of 99% ensures the reliability and robustness of the API.Furthermore, the implementation of Swagger ensures clear and concise API documentation, facilitating ease of use API.
