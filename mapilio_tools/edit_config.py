import os

from . import login
from . import api_v1
from . import config


def edit_config(
    config_file=None,
    user_name=None,
    user_email=None,
    user_password=None,
    jwt=None,
    force_overwrite=False,
    user_key=None,
):
    if config_file is None:
        config_file = config.MAPILIO_CONFIG_PATH

    if not os.path.isfile(config_file):
        config.create_config(config_file)

    if jwt:
        if user_name is None or user_key is None:
            # FIXME: v4 support here
            # user = api_v3.get_user(jwt)
            # user_name = user["username"]
            # user_key = user["key"]
            pass

        user_items = {
            "SettingsUsername": user_name,
            "SettingsUserKey": user_key,
            "user_upload_token": jwt,
        }

        config.update_config(config_file, user_name, user_items)
        return

    if user_key and user_name:  # Manually add user_key
        user_items = {
            "SettingsUsername": "Dummy_SettingsUsername",
            "SettingsUserKey": user_key,
            "user_upload_token": "Dummy_upload_token",
        }
        config.update_config(config_file, user_name, user_items)
        return

    if not user_name:
        user_name = input(
            "Enter the Mapilio mail you would like to (re)authenticate: "
        )

    # config file must exist at this step
    config_object = config.load_config(config_file)

    # safety check if section exists, otherwise add it
    if user_name in config_object.sections():
        if not force_overwrite:
            print("Warning, mail exists with the following items : ")
            print(config.load_user(config_object, user_name))
            sure = input(
                "Are you sure you would like to re-authenticate (current parameters will be overwritten) [y,Y,yes,Yes]?"
            )
            if sure not in ["y", "Y", "yes", "Yes"]:
                print(
                    f"Aborting re-authentication. If you would like to re-authenticate mail {user_name}, "
                    f"rerun this command and confirm re-authentication."
                )
                return
    else:
        config_object.add_section(user_name)

    if user_email and user_password:
        data = api_v1.get_upload_token(user_email, user_password)
        upload_token = data["token"]
        user_key = data["id"]

        if not upload_token:
            raise RuntimeError(
                f"Authentication failed for username {user_name}, please try again."
            )

        user_items = {
            "SettingsUsername": user_name,
            "SettingsUserKey": user_key,
            "user_upload_token": upload_token,
        }
    else:
        # fill in the items and save
        user_items = login.prompt_user_for_user_items(user_name)

    config.update_config(config_file, user_name, user_items)
