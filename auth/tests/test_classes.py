from classes import *
from pathlib import Path
from shutil import rmtree

import unittest


class TestJWTAccessTokens(unittest.TestCase):
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


class TestKeyFolder(unittest.TestCase):
    test_key_folder = f'tests/{KeyFolder.KEY_FOLDER}'
    private = 'private'
    public = 'public'

    def setUp(self):
        KeyFolder.KEY_FOLDER = self.test_key_folder

    def tearDown(self):
        rmtree(KeyFolder.get_key_folder())

    def test_get_key_folder_when_key_folder_does_not_exist_expected_key_folder_created(self):
        # Arrange + an assert that the folders should be removed!
        expected_path_to_key_folder = Path.cwd() / KeyFolder.KEY_FOLDER
        self.assertFalse(expected_path_to_key_folder.exists())

        # Act
        actual_path_to_key_folder = KeyFolder.get_key_folder()
        
        # Assert
        self.assertEquals(expected_path_to_key_folder, actual_path_to_key_folder, 'Since both paths should refer to the same directory')
        self.assertTrue(actual_path_to_key_folder.exists(), 'Since the method also creates the folder if it did not exist')
    
    def test_get_private_key_folder_when_private_key_folder_does_not_exist_expected_private_key_folder_created(self):
        # Arrange + an assert that the folders should be removed!
        expected_path_to_private_key_folder = Path.cwd() / self.test_key_folder / self.private
        self.assertFalse(expected_path_to_private_key_folder.exists())

        # Act
        actual_path_to_private_key_folder = KeyFolder.get_private_key_folder()
        
        # Assert
        self.assertEquals(expected_path_to_private_key_folder, actual_path_to_private_key_folder, 'Since both paths should refer to the same directory')
        self.assertTrue(actual_path_to_private_key_folder.exists(), 'Since the method also creates the folder if it did not exist')
    
    def test_get_public_key_folder_when_public_key_folder_does_not_exist_expected_public_key_folder_created(self):
        # Arrange + an assert that the folders should be removed!
        expected_path_to_public_key_folder = Path.cwd() / self.test_key_folder / self.public
        self.assertFalse(expected_path_to_public_key_folder.exists())

        # Act
        actual_path_to_public_key_folder = KeyFolder.get_public_key_folder()
        
        # Assert
        self.assertEquals(expected_path_to_public_key_folder, actual_path_to_public_key_folder, 'Since both paths should refer to the same directory')
        self.assertTrue(actual_path_to_public_key_folder.exists(), 'Since the method also creates the folder if it did not exist')
    

class KeyGenerator(unittest.TestCase):
    pass
    # After instantiating, should have generated a private and public key pair

class KeyFileWriter(unittest.TestCase):
    pass
    # Writing both private and public keys should make the files exist with data.


if __name__ == '__main__':
    unittest.main()
