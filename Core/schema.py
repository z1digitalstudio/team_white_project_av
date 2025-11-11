import graphene
from user.schema import Query as UserQuery, Mutation as UserMutation
from tag.schema import Query as TagQuery, Mutation as TagMutation
from blog.schema import Query as BlogQuery, Mutation as BlogMutation

class Query (UserQuery, TagQuery, BlogQuery, graphene.ObjectType):
    pass

class Mutation(UserMutation, TagMutation, BlogMutation, graphene.ObjectType):
    pass

schema = graphene.Schema(query=Query, mutation=Mutation)
