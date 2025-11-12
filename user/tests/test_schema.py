from blog.tests.factories import UserFactory
from Core.tests import GraphQLTestCase
from unittest.mock import Mock
from django.contrib.auth.models import User


class TestQuery(GraphQLTestCase):
    def setUp(self):
        super().setUp()
        self.user = UserFactory()

    def test_query_all_users(self):
        query = """
        query {
            allUsers {
                id
                username
                email
            }
        }
        """
        result = self.client.execute(query)

        self.assertIsNone(result.get("errors"), result.get("errors"))

        users = result["data"]["allUsers"]
        self.assertEqual(len(users), 1)
        self.assertEqual(int(users[0]["id"]), self.user.id)
        self.assertEqual(users[0]["username"], self.user.username)
   
    def test_query_user_by_id_found(self):
        query = f"""
        query {{
            userById(id: {self.user.id}) {{
                id
                username
            }}
        }}
        """
        result = self.client.execute(query)
        self.assertIsNone(result.get("errors"), result.get("errors"))
        self.assertIsNotNone(result["data"]["userById"])
        self.assertEqual(int(result["data"]["userById"]["id"]), self.user.id)
        self.assertEqual(result["data"]["userById"]["username"], self.user.username)

    def test_query_user_by_id_not_found(self):
        query = """
        query {
            userById(id: 9999) {
                id
                username
            }
        }
        """
        result = self.client.execute(query)
        self.assertIsNotNone(result.get("errors"))
        self.assertIn("User not found", str(result["errors"][0]["message"]))


class TestMutation(GraphQLTestCase):
    def setUp(self):
        super().setUp()
        self.user = UserFactory(password="password")

    def test_mutation_create_user(self):
        query = """
        mutation {
            createUser(
                username: "nuevo"
                email: "nuevo@example.com"
                password: "pass"
                passwordConfirm: "pass"
            ) {
                user {
                    id
                    username
                    email
                }
            }
        }
        """
        result = self.client.execute(query)
        self.assertIsNone(result.get("errors"), result.get("errors"))

        user_data = result["data"]["createUser"]["user"]
        self.assertEqual(user_data["username"], "nuevo")
        self.assertEqual(user_data["email"], "nuevo@example.com")

    def test_mutation_user_already_exists(self):
        query = f"""
        mutation {{
            createUser(
                username: "{self.user.username}"
                email: "{self.user.email}"
                password: "password"
                passwordConfirm: "password"
            ) {{
                user {{
                    id
                }}
            }}
        }}
        """
        result = self.client.execute(query)
        self.assertIsNotNone(result.get("errors"))

    def test_mutation_login_user(self):
        query = f"""
        mutation {{
            loginUser(username: "{self.user.username}", password: "password") {{
                token
                user {{
                    username
                }}
            }}
        }}
        """
        result = self.client.execute(query)
        self.assertIsNone(result.get("errors"), result.get("errors"))
        self.assertEqual(result["data"]["loginUser"]["user"]["username"], self.user.username)

    def test_mutation_login_invalid_credentials(self):
        query = f"""
        mutation {{
            loginUser(username: "{self.user.username}", password: "wrong_password") {{
                token
                user {{
                    username
                }}
            }}
        }}
        """
        result = self.client.execute(query)
        self.assertIsNotNone(result.get("errors"))

    def test_mutation_delete_user(self):
        login_query = f"""
        mutation {{
            loginUser(username: "{self.user.username}", password: "password") {{
                token
            }}
        }}
        """
        login_result = self.client.execute(login_query)
        token = login_result["data"]["loginUser"]["token"]
        
        context = Mock()
        context.headers = {"Authorization": f"Bearer {token}"}
        
        user_id = self.user.id
        
        query = f"""
        mutation {{
            deleteUser(userId: {user_id}) {{
                user {{
                    username
                }}
            }}
        }}
        """
        result = self.client.execute(query, context_value=context)
        self.assertIsNone(result.get("errors"), result.get("errors"))
        self.assertIn("deleteUser", result["data"])
        self.assertFalse(User.objects.filter(id=user_id).exists())


    def test_mutation_update_password(self):
        login_query = f"""
        mutation {{
            loginUser(username: "{self.user.username}", password: "password") {{
                token
            }}
        }}
        """
        login_result = self.client.execute(login_query)
        token = login_result["data"]["loginUser"]["token"]
        
        context = Mock()
        context.headers = {"Authorization": f"Bearer {token}"}
        
        query = """
        mutation {
            updatePassword(newPassword: "newpass", confirmPassword: "newpass") {
                success
            }
        }
        """
        result = self.client.execute(query, context_value=context)
        self.assertIsNone(result.get("errors"), result.get("errors"))
        self.assertTrue(result["data"]["updatePassword"]["success"])
