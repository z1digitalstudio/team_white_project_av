from blog.tests.factories import UserFactory, BlogFactory, PostFactory, TagFactory
from Core.tests import GraphQLTestCase
from unittest.mock import Mock
from tag.models import Tag
from blog.models import Post


class TestTagQuery(GraphQLTestCase):
    def setUp(self):
        super().setUp()
        self.tag1 = TagFactory(name="python")
        self.tag2 = TagFactory(name="django")
        self.tag3 = TagFactory(name="javascript")

    def test_query_all_tags(self):
        query = """
        query {
            tags {
                id
                name
            }
        }
        """
        result = self.client.execute(query)
        self.assertIsNone(result.get("errors"), result.get("errors"))
        tags = result["data"]["tags"]
        self.assertGreaterEqual(len(tags), 3)

    def test_query_tag_by_id_found(self):
        query = f"""
        query {{
            tag(id: {self.tag1.id}) {{
                id
                name
            }}
        }}
        """
        result = self.client.execute(query)
        self.assertIsNone(result.get("errors"), result.get("errors"))
        self.assertIsNotNone(result["data"]["tag"])
        self.assertEqual(int(result["data"]["tag"]["id"]), self.tag1.id)
        self.assertEqual(result["data"]["tag"]["name"], self.tag1.name)

    def test_query_tag_by_id_not_found(self):
        query = """
        query {
            tag(id: 9999) {
                id
                name
            }
        }
        """
        result = self.client.execute(query)
        self.assertIsNotNone(result.get("errors"))
        self.assertIn("Tag not found", str(result["errors"][0]["message"]))

    def test_query_tags_by_name(self):
        query = """
        query {
            tagsByName(name: "python") {
                id
                name
            }
        }
        """
        result = self.client.execute(query)
        self.assertIsNone(result.get("errors"), result.get("errors"))
        tags = result["data"]["tagsByName"]
        self.assertGreaterEqual(len(tags), 1)

    def test_query_posts_by_tag(self):
        user = UserFactory()
        blog = BlogFactory(user=user)
        post = PostFactory(blog=blog)
        post.tags.add(self.tag1)
        
        query = f"""
        query {{
            postsByTag(id: {self.tag1.id}) {{
                id
                title
            }}
        }}
        """
        result = self.client.execute(query)
        self.assertIsNone(result.get("errors"), result.get("errors"))
        posts = result["data"]["postsByTag"]
        self.assertGreaterEqual(len(posts), 1)

    def test_query_tags_by_post(self):
        user = UserFactory()
        blog = BlogFactory(user=user)
        post = PostFactory(blog=blog)
        post.tags.add(self.tag1, self.tag2)
        
        query = f"""
        query {{
            tagsByPost(id: {post.id}) {{
                id
                name
            }}
        }}
        """
        result = self.client.execute(query)
        self.assertIsNone(result.get("errors"), result.get("errors"))
        tags = result["data"]["tagsByPost"]
        self.assertEqual(len(tags), 2)

    def test_query_tags_by_post_name(self):
        user = UserFactory()
        blog = BlogFactory(user=user)
        post = PostFactory(blog=blog, title="Test Post")
        post.tags.add(self.tag1)
        
        query = """
        query {
            tagsByPostName(postName: "Test Post") {
                id
                name
            }
        }
        """
        result = self.client.execute(query)
        self.assertIsNone(result.get("errors"), result.get("errors"))
        tags = result["data"]["tagsByPostName"]
        self.assertGreaterEqual(len(tags), 1)

    def test_query_tags_by_name_and_post_id(self):
        user = UserFactory()
        blog = BlogFactory(user=user)
        post = PostFactory(blog=blog)
        post.tags.add(self.tag1)
        
        query = f"""
        query {{
            tagsByNameAndPostId(name: "python", postId: {post.id}) {{
                id
                name
            }}
        }}
        """
        result = self.client.execute(query)
        self.assertIsNone(result.get("errors"), result.get("errors"))
        tags = result["data"]["tagsByNameAndPostId"]
        self.assertGreaterEqual(len(tags), 1)

    def test_query_tags_by_name_and_post_name(self):
        user = UserFactory()
        blog = BlogFactory(user=user)
        post = PostFactory(blog=blog, title="Test Post")
        post.tags.add(self.tag1)
        
        query = """
        query {
            tagsByNameAndPostName(name: "python", postName: "Test Post") {
                id
                name
            }
        }
        """
        result = self.client.execute(query)
        self.assertIsNone(result.get("errors"), result.get("errors"))
        tags = result["data"]["tagsByNameAndPostName"]
        self.assertGreaterEqual(len(tags), 1)


class TestTagMutation(GraphQLTestCase):
    def setUp(self):
        super().setUp()
        self.user = UserFactory(password="password")

    def _get_authenticated_context(self, user):
        """Helper method to get authenticated context"""
        login_query = f"""
        mutation {{
            loginUser(username: "{user.username}", password: "password") {{
                token
            }}
        }}
        """
        login_result = self.client.execute(login_query)
        token = login_result["data"]["loginUser"]["token"]
        context = Mock()
        context.headers = {"Authorization": f"Bearer {token}"}
        return context

    def test_mutation_create_tag(self):
        context = self._get_authenticated_context(self.user)
        query = """
        mutation {
            createTag(name: "newtag") {
                tag {
                    id
                    name
                }
                success
            }
        }
        """
        result = self.client.execute(query, context_value=context)
        self.assertIsNone(result.get("errors"), result.get("errors"))
        tag_data = result["data"]["createTag"]["tag"]
        self.assertEqual(tag_data["name"], "newtag")
        self.assertTrue(result["data"]["createTag"]["success"])

    def test_mutation_create_tag_not_authenticated(self):
        query = """
        mutation {
            createTag(name: "newtag") {
                tag {
                    id
                }
            }
        }
        """
        result = self.client.execute(query)
        self.assertIsNotNone(result.get("errors"))

    def test_mutation_create_tag_empty_name(self):
        context = self._get_authenticated_context(self.user)
        query = """
        mutation {
            createTag(name: "") {
                tag {
                    id
                }
            }
        }
        """
        result = self.client.execute(query, context_value=context)
        self.assertIsNotNone(result.get("errors"))

    def test_mutation_update_tag(self):
        tag = TagFactory()
        context = self._get_authenticated_context(self.user)
        query = f"""
        mutation {{
            updateTag(id: {tag.id}, name: "updated_tag") {{
                tag {{
                    id
                    name
                }}
                success
            }}
        }}
        """
        result = self.client.execute(query, context_value=context)
        self.assertIsNone(result.get("errors"), result.get("errors"))
        tag_data = result["data"]["updateTag"]["tag"]
        self.assertEqual(tag_data["name"], "updated_tag")
        self.assertTrue(result["data"]["updateTag"]["success"])

    def test_mutation_update_tag_not_found(self):
        context = self._get_authenticated_context(self.user)
        query = """
        mutation {
            updateTag(id: 9999, name: "updated_tag") {
                tag {
                    id
                }
            }
        }
        """
        result = self.client.execute(query, context_value=context)
        self.assertIsNotNone(result.get("errors"))

    def test_mutation_delete_tag(self):
        tag = TagFactory()
        context = self._get_authenticated_context(self.user)
        tag_id = tag.id
        query = f"""
        mutation {{
            deleteTag(id: {tag_id}) {{
                success
                message
            }}
        }}
        """
        result = self.client.execute(query, context_value=context)
        self.assertIsNone(result.get("errors"), result.get("errors"))
        self.assertTrue(result["data"]["deleteTag"]["success"])
        self.assertFalse(Tag.objects.filter(id=tag_id).exists())


class TestTagPostMutation(GraphQLTestCase):
    def setUp(self):
        super().setUp()
        self.user = UserFactory(password="password")
        self.other_user = UserFactory(password="password")
        self.blog = BlogFactory(user=self.user)
        self.post = PostFactory(blog=self.blog)
        self.tag = TagFactory()

    def _get_authenticated_context(self, user):
        """Helper method to get authenticated context"""
        login_query = f"""
        mutation {{
            loginUser(username: "{user.username}", password: "password") {{
                token
            }}
        }}
        """
        login_result = self.client.execute(login_query)
        token = login_result["data"]["loginUser"]["token"]
        context = Mock()
        context.headers = {"Authorization": f"Bearer {token}"}
        return context

    def test_mutation_add_tag_to_post(self):
        context = self._get_authenticated_context(self.user)
        query = f"""
        mutation {{
            addTagToPost(postId: {self.post.id}, tagId: {self.tag.id}) {{
                post {{
                    id
                }}
                tag {{
                    id
                }}
                success
            }}
        }}
        """
        result = self.client.execute(query, context_value=context)
        self.assertIsNone(result.get("errors"), result.get("errors"))
        self.assertTrue(result["data"]["addTagToPost"]["success"])
        self.assertTrue(self.post.tags.filter(id=self.tag.id).exists())

    def test_mutation_add_tag_to_post_permission_denied(self):
        other_blog = BlogFactory(user=self.other_user)
        other_post = PostFactory(blog=other_blog)
        context = self._get_authenticated_context(self.user)
        query = f"""
        mutation {{
            addTagToPost(postId: {other_post.id}, tagId: {self.tag.id}) {{
                post {{
                    id
                }}
            }}
        }}
        """
        result = self.client.execute(query, context_value=context)
        self.assertIsNotNone(result.get("errors"))

    def test_mutation_add_tag_to_post_not_found(self):
        context = self._get_authenticated_context(self.user)
        query = """
        mutation {
            addTagToPost(postId: 9999, tagId: 9999) {
                post {
                    id
                }
            }
        }
        """
        result = self.client.execute(query, context_value=context)
        self.assertIsNotNone(result.get("errors"))

    def test_mutation_remove_tag_from_post(self):
        self.post.tags.add(self.tag)
        context = self._get_authenticated_context(self.user)
        query = f"""
        mutation {{
            removeTagFromPost(postId: {self.post.id}, tagId: {self.tag.id}) {{
                post {{
                    id
                }}
                tag {{
                    id
                }}
                success
            }}
        }}
        """
        result = self.client.execute(query, context_value=context)
        self.assertIsNone(result.get("errors"), result.get("errors"))
        self.assertTrue(result["data"]["removeTagFromPost"]["success"])
        self.assertFalse(self.post.tags.filter(id=self.tag.id).exists())

    def test_mutation_remove_tag_from_post_permission_denied(self):
        other_blog = BlogFactory(user=self.other_user)
        other_post = PostFactory(blog=other_blog)
        other_post.tags.add(self.tag)
        context = self._get_authenticated_context(self.user)
        query = f"""
        mutation {{
            removeTagFromPost(postId: {other_post.id}, tagId: {self.tag.id}) {{
                post {{
                    id
                }}
            }}
        }}
        """
        result = self.client.execute(query, context_value=context)
        self.assertIsNotNone(result.get("errors"))

