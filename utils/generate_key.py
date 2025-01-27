import pickle
from pathlib import Path

import streamlit_authenticator as stauth

names = ["Eddy", "Diego", "Francisco"]
usernames = ["eddy", "diego", "francisco"]
passwords = ["1234", "1234", "1234"]

hashed_passwords = stauth.Hasher(passwords)

with open(Path(__file__).parent / "hashed_pw.pkl", "wb") as f:
    pickle.dump(hashed_passwords, f)