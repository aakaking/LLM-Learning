import getpass
import os

def get_nv_api_key():
    if os.environ.get("NVIDIA_API_KEY", "").startswith("nvapi-"):
        print("Valid NVIDIA_API_KEY already in environment. Delete to reset")
    else:
        nvapi_key = getpass.getpass("NVAPI Key (starts with nvapi-): ")
        assert nvapi_key.startswith("nvapi-"), f"{nvapi_key[:5]}... is not a valid key"
        os.environ["NVIDIA_API_KEY"] = nvapi_key
    return nvapi_key