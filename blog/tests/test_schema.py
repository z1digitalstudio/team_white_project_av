from blog.tests.factories import UserFactory, BlogFactory, PostFactory, TagFactory
from Core.tests import GraphQLTestCase
from unittest.mock import Mock
from blog.models import Blog, Post
from tag.models import Tag


class TestBlogQuery(GraphQLTestCase):
    def setUp(self):
        super().setUp()
        self.user = UserFactory()
        self.blog = BlogFactory(user=self.user)
        self.other_user = UserFactory()
        self.other_blog = BlogFactory(user=self.other_user)

    def test_query_all_blogs(self):
        query = """
        query {
            blogs {
                id
                title
                description
            }
        }
        """
        result = self.client.execute(query)
        self.assertIsNone(result.get("errors"), result.get("errors"))
        blogs = result["data"]["blogs"]
        self.assertEqual(len(blogs), 2)

    def test_query_blog_by_id_found(self):
        query = f"""
        query {{
            blog(id: {self.blog.id}) {{
                id
                title
                description
            }}
        }}
        """
        result = self.client.execute(query)
        self.assertIsNone(result.get("errors"), result.get("errors"))
        self.assertIsNotNone(result["data"]["blog"])
        self.assertEqual(int(result["data"]["blog"]["id"]), self.blog.id)
        self.assertEqual(result["data"]["blog"]["title"], self.blog.title)

    def test_query_blogs_by_user(self):
        query = f"""
        query {{
            blogsByUser(userId: {self.user.id}) {{
                id
                title
            }}
        }}
        """
        result = self.client.execute(query)
        self.assertIsNone(result.get("errors"), result.get("errors"))
        blogs = result["data"]["blogsByUser"]
        self.assertEqual(len(blogs), 1)
        self.assertEqual(int(blogs[0]["id"]), self.blog.id)

    def test_query_blogs_by_title(self):
        query = f"""
        query {{
            blogsByTitle(title: "{self.blog.title[:10]}") {{
                id
                title
            }}
        }}
        """
        result = self.client.execute(query)
        self.assertIsNone(result.get("errors"), result.get("errors"))
        blogs = result["data"]["blogsByTitle"]
        self.assertGreaterEqual(len(blogs), 1)


class TestPostQuery(GraphQLTestCase):
    def setUp(self):
        super().setUp()
        self.user = UserFactory()
        self.blog = BlogFactory(user=self.user)
        self.post = PostFactory(blog=self.blog)
        self.other_post = PostFactory(blog=self.blog)

    def test_query_all_posts(self):
        query = """
        query {
            posts {
                id
                title
                content
            }
        }
        """
        result = self.client.execute(query)
        self.assertIsNone(result.get("errors"), result.get("errors"))
        posts = result["data"]["posts"]
        self.assertGreaterEqual(len(posts), 2)

    def test_query_post_by_id_found(self):
        query = f"""
        query {{
            post(id: {self.post.id}) {{
                id
                title
                content
            }}
        }}
        """
        result = self.client.execute(query)
        self.assertIsNone(result.get("errors"), result.get("errors"))
        self.assertIsNotNone(result["data"]["post"])
        self.assertEqual(int(result["data"]["post"]["id"]), self.post.id)
        self.assertEqual(result["data"]["post"]["title"], self.post.title)

    def test_query_post_by_id_not_found(self):
        query = """
        query {
            post(id: 9999) {
                id
                title
            }
        }
        """
        result = self.client.execute(query)
        self.assertIsNotNone(result.get("errors"))
        self.assertIn("Post not found", str(result["errors"][0]["message"]))

    def test_query_posts_by_blog(self):
        query = f"""
        query {{
            postsByBlog(blogId: {self.blog.id}) {{
                id
                title
            }}
        }}
        """
        result = self.client.execute(query)
        self.assertIsNone(result.get("errors"), result.get("errors"))
        posts = result["data"]["postsByBlog"]
        self.assertGreaterEqual(len(posts), 2)

    def test_query_posts_by_title(self):
        query = f"""
        query {{
            postsByTitle(title: "{self.post.title[:10]}") {{
                id
                title
            }}
        }}
        """
        result = self.client.execute(query)
        self.assertIsNone(result.get("errors"), result.get("errors"))
        posts = result["data"]["postsByTitle"]
        self.assertGreaterEqual(len(posts), 1)

    def test_query_posts_by_user(self):
        user = UserFactory(password="password")
        blog = BlogFactory(user=user)
        post = PostFactory(blog=blog)
        
        # Get authenticated context
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
        
        query = f"""
        query {{
            postsByUser(userId: {user.id}) {{
                id
                title
            }}
        }}
        """
        result = self.client.execute(query, context_value=context)
        self.assertIsNone(result.get("errors"), result.get("errors"))
        posts = result["data"]["postsByUser"]
        self.assertGreaterEqual(len(posts), 1)

    def test_query_posts_by_user_not_authenticated(self):
        user = UserFactory()
        query = f"""
        query {{
            postsByUser(userId: {user.id}) {{
                id
                title
            }}
        }}
        """
        result = self.client.execute(query)
        self.assertIsNotNone(result.get("errors"))


class TestBlogMutation(GraphQLTestCase):
    def setUp(self):
        super().setUp()
        self.user = UserFactory(password="password")
        self.other_user = UserFactory(password="password")

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

    def test_mutation_create_blog(self):
        context = self._get_authenticated_context(self.user)
        query = """
        mutation {
            createBlog(title: "My Blog", description: "Blog description") {
                blog {
                    id
                    title
                    description
                }
                success
            }
        }
        """
        result = self.client.execute(query, context_value=context)
        self.assertIsNone(result.get("errors"), result.get("errors"))
        blog_data = result["data"]["createBlog"]["blog"]
        self.assertEqual(blog_data["title"], "My Blog")
        self.assertEqual(blog_data["description"], "Blog description")
        self.assertTrue(result["data"]["createBlog"]["success"])

    def test_mutation_create_blog_not_authenticated(self):
        query = """
        mutation {
            createBlog(title: "My Blog", description: "Blog description") {
                blog {
                    id
                }
            }
        }
        """
        result = self.client.execute(query)
        self.assertIsNotNone(result.get("errors"))

    def test_mutation_create_blog_empty_title(self):
        context = self._get_authenticated_context(self.user)
        query = """
        mutation {
            createBlog(title: "", description: "Blog description") {
                blog {
                    id
                }
            }
        }
        """
        result = self.client.execute(query, context_value=context)
        self.assertIsNotNone(result.get("errors"))

    def test_mutation_update_blog(self):
        blog = BlogFactory(user=self.user)
        context = self._get_authenticated_context(self.user)
        query = f"""
        mutation {{
            updateBlog(id: {blog.id}, title: "Updated Title", description: "Updated description") {{
                blog {{
                    id
                    title
                    description
                }}
                success
            }}
        }}
        """
        result = self.client.execute(query, context_value=context)
        self.assertIsNone(result.get("errors"), result.get("errors"))
        blog_data = result["data"]["updateBlog"]["blog"]
        self.assertEqual(blog_data["title"], "Updated Title")
        self.assertEqual(blog_data["description"], "Updated description")
        self.assertTrue(result["data"]["updateBlog"]["success"])

    def test_mutation_update_blog_permission_denied(self):
        blog = BlogFactory(user=self.other_user)
        context = self._get_authenticated_context(self.user)
        query = f"""
        mutation {{
            updateBlog(id: {blog.id}, title: "Updated Title", description: "Updated description") {{
                blog {{
                    id
                }}
            }}
        }}
        """
        result = self.client.execute(query, context_value=context)
        self.assertIsNotNone(result.get("errors"))

    def test_mutation_delete_blog(self):
        blog = BlogFactory(user=self.user)
        context = self._get_authenticated_context(self.user)
        blog_id = blog.id
        query = f"""
        mutation {{
            deleteBlog(id: {blog_id}) {{
                success
                message
            }}
        }}
        """
        result = self.client.execute(query, context_value=context)
        self.assertIsNone(result.get("errors"), result.get("errors"))
        self.assertTrue(result["data"]["deleteBlog"]["success"])
        self.assertFalse(Blog.objects.filter(id=blog_id).exists())


class TestPostMutation(GraphQLTestCase):
    def setUp(self):
        super().setUp()
        self.user = UserFactory(password="password")
        self.blog = BlogFactory(user=self.user)
        self.other_user = UserFactory(password="password")
        self.other_blog = BlogFactory(user=self.other_user)

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

    def test_mutation_create_post(self):
        context = self._get_authenticated_context(self.user)
        query = f"""
        mutation {{
            createPost(blogId: {self.blog.id}, title: "My Post", content: "Post content") {{
                post {{
                    id
                    title
                    content
                }}
                success
            }}
        }}
        """
        result = self.client.execute(query, context_value=context)
        self.assertIsNone(result.get("errors"), result.get("errors"))
        post_data = result["data"]["createPost"]["post"]
        self.assertEqual(post_data["title"], "My Post")
        self.assertEqual(post_data["content"], "Post content")
        self.assertTrue(result["data"]["createPost"]["success"])

    def test_mutation_create_post_not_authenticated(self):
        query = f"""
        mutation {{
            createPost(blogId: {self.blog.id}, title: "My Post", content: "Post content") {{
                post {{
                    id
                }}
            }}
        }}
        """
        result = self.client.execute(query)
        self.assertIsNotNone(result.get("errors"))

    def test_mutation_create_post_blog_not_found(self):
        context = self._get_authenticated_context(self.user)
        query = """
        mutation {
            createPost(blogId: 9999, title: "My Post", content: "Post content") {
                post {
                    id
                }
            }
        }
        """
        result = self.client.execute(query, context_value=context)
        self.assertIsNotNone(result.get("errors"))

    def test_mutation_update_post(self):
        post = PostFactory(blog=self.blog)
        context = self._get_authenticated_context(self.user)
        query = f"""
        mutation {{
            updatePost(id: {post.id}, title: "Updated Post", content: "Updated content") {{
                post {{
                    id
                    title
                    content
                }}
                success
            }}
        }}
        """
        result = self.client.execute(query, context_value=context)
        self.assertIsNone(result.get("errors"), result.get("errors"))
        post_data = result["data"]["updatePost"]["post"]
        self.assertEqual(post_data["title"], "Updated Post")
        self.assertEqual(post_data["content"], "Updated content")
        self.assertTrue(result["data"]["updatePost"]["success"])

    def test_mutation_update_post_permission_denied(self):
        other_post = PostFactory(blog=self.other_blog)
        context = self._get_authenticated_context(self.user)
        query = f"""
        mutation {{
            updatePost(id: {other_post.id}, title: "Updated Post", content: "Updated content") {{
                post {{
                    id
                }}
            }}
        }}
        """
        result = self.client.execute(query, context_value=context)
        self.assertIsNotNone(result.get("errors"))

    def test_mutation_delete_post(self):
        post = PostFactory(blog=self.blog)
        context = self._get_authenticated_context(self.user)
        post_id = post.id
        query = f"""
        mutation {{
            deletePost(id: {post_id}) {{
                success
                message
            }}
        }}
        """
        result = self.client.execute(query, context_value=context)
        self.assertIsNone(result.get("errors"), result.get("errors"))
        self.assertTrue(result["data"]["deletePost"]["success"])
        self.assertFalse(Post.objects.filter(id=post_id).exists())


class TestPostTagMutation(GraphQLTestCase):
    def setUp(self):
        super().setUp()
        self.user = UserFactory(password="password")
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

