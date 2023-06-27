
from flask_dance.consumer import OAuth2ConsumerBlueprint, oauth_authorized, oauth_error
from flask_smorest import Blueprint, abort
from flask.views import MethodView
import requests


# Amazon OAuth configuration
client_id = "amzn1.application-oa2-client.c7cf91a7a14e4617b2219160850b0ee2"
client_secret = "amzn1.oa2-cs.v1.ecf9473f1ba98315a023e2e24dcef03fe0f3850bcfa89abe22b40a9b4c1d17f9"
authorization_url = "https://www.amazon.com/ap/oa"
token_url = "https://api.amazon.com/auth/o2/token"
redirect_url = "https://127.0.0.1:5001/token"

amazon_blueprint = OAuth2ConsumerBlueprint(
    "amazon",
    __name__,
    client_id=client_id,
    client_secret=client_secret,
    authorization_url=authorization_url,
    token_url=token_url,
    redirect_url=redirect_url,
    scope=["profile"],
    response_type=["code"],
    # "scope": "profile",
    # authorization_kwargs={"response_type": "code"},
)

blp = Blueprint("UsersLogin", __name__, description="Authenticate users")

amazon_params = {
    "client_id": client_id,
    "scope": "profile",
    "response_type": "code",
    "redirect_uri": redirect_url,
}
# amazon_auth_str = authorization_url + urlencode(amazon_params)
amazon_auth_str = f"{authorization_url}?client_id={client_id}&scope=profile&response_type=code&redirect_uri={redirect_url}"


@blp.route("/callback")
class AmazonCallbackResource(MethodView):

    # @blp.response(200, "Success")
    def get(self):
        if not amazon_blueprint.session.authorized:
            abort(401, message="Authorization failed.")

        # Get the access token using the authorization code
        amazon_blueprint.session.fetch_token(
            token_url=token_url,
            authorization_response=requests.request.url,
        )

        # Make a request to the user profile endpoint
        response = amazon_blueprint.session.get("/user/profile")
        if response.ok:
            profile_data = response.json()
            return profile_data
        else:
            abort(500, message="Failed to retrieve user profile.")

