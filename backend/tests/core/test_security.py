from app.core.security import get_password_hash, verify_password


def test_verify_password():
    """
    Test for password verification.
    """
    password = "supersecretpassword"
    hashed_password = get_password_hash(password)

    # Assert hashed_password is different from password
    assert hashed_password != password
    # Assert that if the correct password passes verification
    assert verify_password(password, hashed_password)
    # Assert the wrong password fails verification
    assert not verify_password("notsosecretpassword", hashed_password)
