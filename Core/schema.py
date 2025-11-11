import graphene
from user.schema import Query as UserQuery, Mutation as UserMutation
from tag.schema import Query as TagQuery, Mutation as TagMutation

class Query (UserQuery, TagQuery, graphene.ObjectType):
    pass

class Mutation(UserMutation, TagMutation, graphene.ObjectType):
    pass

schema = graphene.Schema(query=Query, mutation=Mutation)
