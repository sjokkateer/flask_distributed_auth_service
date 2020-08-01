from classes import JWT, Token, InvalidTokenTypeException

import unittest


class TestJWTAccessTokens(unittest.TestCase):
    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        db.create_all()

        # Should create some keys

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_get_ttl_for_access_token(self):
        # Arrange
        ttl = JWT.get_ttl(Token.ACCESS)
        expected_ttl_of_access_token_in_minutes = 15
        
        # Act
        actual_ttl_of_access_token_in_minutes = ttl.seconds / 60 # Since timedelta converts minutes into seconds behind the scene

        # Assert
        self.assertEqual(
            actual_ttl_of_access_token_in_minutes, 
            expected_ttl_of_access_token_in_minutes, 
            f'TTL of access token should equal {expected_ttl_of_access_token_in_minutes} but was {actual_ttl_of_access_token_in_minutes}.')

    def test_get_ttl_for_refresh_token(self):
        # Arrange
        ttl = JWT.get_ttl(Token.REFRESH)
        expected_ttl_of_refresh_token_in_days = 30
        
        # Act
        actual_ttl_of_refresh_token_in_days = ttl.days

        # Assert
        self.assertEqual(
            actual_ttl_of_refresh_token_in_days, 
            expected_ttl_of_refresh_token_in_days, 
            f'TTL of refresh token should equal {expected_ttl_of_refresh_token_in_days} but was {actual_ttl_of_refresh_token_in_days}.')


    def test_get_ttl_for_invalid_data(self):
        # Arrange, Act, Assert
        self.assertRaises(InvalidTokenTypeException)


if __name__ == '__main__':
    unittest.main()
