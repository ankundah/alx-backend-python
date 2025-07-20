#!/usr/bin/env python3
"""Unit tests for the GithubOrgClient class."""

import unittest
from parameterized import parameterized
from unittest.mock import patch, Mock, PropertyMock
from client import GithubOrgClient
from parameterized import parameterized_class

# Assuming fixtures are imported from fixtures.py
from fixtures import org_payload, repos_payload, expected_repos, apache2_repos

@parameterized_class(('org_payload', 'repos_payload', 'expected_repos', 'apache2_repos'), [
    (org_payload, repos_payload, expected_repos, apache2_repos),
])


class TestGithubOrgClient(unittest.TestCase):
    """Test cases for the GithubOrgClient class."""

    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @patch('client.get_json')
    def test_org(self, org_name, mock_get_json):
        """Test that GithubOrgClient.org returns correct value and makes proper API call."""
        # Set up the mock return value
        test_payload = {"name": org_name, "repos_url": f"https://api.github.com/orgs/{org_name}/repos"}
        mock_get_json.return_value = test_payload

        # Create client instance
        client = GithubOrgClient(org_name)

        # Call the org property
        result = client.org

        # Verify get_json was called once with correct URL
        expected_url = f"https://api.github.com/orgs/{org_name}"
        mock_get_json.assert_called_once_with(expected_url)

        # Verify the result matches the test payload
        self.assertEqual(result, test_payload)

    def test_public_repos_url(self):
        """Test that _public_repos_url returns the correct URL from the org payload."""
        # Define the test payload with a known repos_url
        test_payload = {
            "repos_url": "https://api.github.com/orgs/testorg/repos"
        }
        
        # Create a mock for the org property that returns our test payload
        with patch('client.GithubOrgClient.org', new_callable=PropertyMock) as mock_org:
            mock_org.return_value = test_payload
            
            # Create an instance of the client
            client = GithubOrgClient("testorg")
            
            # Call the _public_repos_url property
            result = client._public_repos_url
            
            # Verify the result matches the expected URL
            self.assertEqual(result, test_payload["repos_url"])
            
            # Verify org property was accessed
            mock_org.assert_called_once()
    
    @patch('client.get_json')

    def test_public_repos(self, mock_get_json):
        """Test that public_repos returns the correct list of repos."""
        # Test data
        test_repo_payload = [
            {"name": "repo1", "license": {"key": "mit"}},
            {"name": "repo2", "license": {"key": "apache-2.0"}},
            {"name": "repo3", "license": None},
        ]
        test_url = "https://api.github.com/orgs/testorg/repos"
        
        # Configure mock for get_json
        mock_get_json.return_value = test_repo_payload
        
        # Mock the _public_repos_url property
        with patch('client.GithubOrgClient._public_repos_url',
                new_callable=PropertyMock) as mock_public_repos_url:
            mock_public_repos_url.return_value = test_url
            
            # Create client instance
            client = GithubOrgClient("testorg")
            
            # Call public_repos
            repos = client.public_repos()
            
            # Verify results
            expected_repos = ["repo1", "repo2", "repo3"]
            self.assertEqual(repos, expected_repos)
            
            # Verify mocks were called once
            mock_public_repos_url.assert_called_once()
            mock_get_json.assert_called_once_with(test_url)

    @parameterized.expand([
    ({"license": {"key": "my_license"}}, "my_license", True),
    ({"license": {"key": "other_license"}}, "my_license", False),
])
    def test_has_license(self, repo, license_key, expected):        
        """Test that has_license returns the correct boolean."""
        result = GithubOrgClient.has_license(repo, license_key)
        self.assertEqual(result, expected)

if __name__ == "__main__":
    unittest.main()

@parameterized_class([
    {
        'org_payload': org_payload,
        'repos_payload': repos_payload,
        'expected_repos': expected_repos,
        'apache2_repos': apache2_repos
    }
])
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration tests for GithubOrgClient."""

    @classmethod
    def setUpClass(cls):
        """Set up class fixtures before running tests."""
        cls.get_patcher = patch('requests.get')
        cls.mock_get = cls.get_patcher.start()

        def side_effect(url):
            """Return different payloads based on URL."""
            if url.endswith('/orgs/google'):
                return Mock(json=lambda: cls.org_payload)
            elif url.endswith('/repos'):
                return Mock(json=lambda: cls.repos_payload)
            return Mock(json=lambda: None)

        cls.mock_get.side_effect = side_effect

    @classmethod
    def tearDownClass(cls):
        """Stop the patcher after tests are done."""
        cls.get_patcher.stop()

    def test_public_repos(self):
        """Test public_repos returns expected repos."""
        client = GithubOrgClient("google")
        repos = client.public_repos()
        self.assertEqual(repos, self.expected_repos)

    def test_public_repos_with_license(self):
        """Test public_repos with license filter."""
        client = GithubOrgClient("google")
        repos = client.public_repos(license="apache-2.0")
        self.assertEqual(repos, self.apache2_repos)    