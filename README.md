# graphql
This is a library for executing [GraphQL](https://facebook.github.io/graphql/)
documents in Python.  It is meant to conform to the April 2016 working draft of
Facebook's GraphQL query language.  It uses Python decorators to specify GraphQL
types, fields, etc.

# Features
* Parse and execute GraphQL documents, including queries and mutations.
* Specify GraphQL types, fields, etc. using Python decorators.  See the below
  example.
* Optionally, extract the schema information from the decorators during
  preprocessing, store it as JSON text, and load it at runtime.
* Lazily import Python modules, at the moment we need them to resolve a GraphQL
  field.  The schema is loaded in memory though, so introspection queries do not
  require us to load any extra modules.

# Limitations
* Currently no support for subscriptions.
* Currently no support for non-null `__InputValue{description, defaultValue}`
  and `__EnumValue{description, deprecationReason}` values and true
  `__EnumValue{isDeprecated}` values.
* Only tested in Python 2.7.
* Potentially unstable API.  At time of writing, this library is new, so please
  bear with me if the API changes quickly.

# Example
Usage:
<pre lang="python">
context = GraphQlContext(get_schema())
print(GraphQlExecutor.execute('{hero{name}}', context))
</pre>

Objects:
<pre lang="python">
@graphql_interface('Character')
@graphql_attr_field('character_id', 'id', 'String!')
@graphql_attr_field('name', 'name', 'String')
@graphql_attr_field('appears_in', 'appearsIn', '[Episode]')
class Character(object):
    def __init__(self, character_id, name, appears_in, friend_ids):
        self.character_id = character_id
        self.name = name
        self.appears_in = appears_in
        self._friend_ids = friend_ids

    @graphql_field('friends', '[Character]')
    def friends(self):
        friends = []
        for friend_id in self._friend_ids:
            friends.append(CharacterFactory.character(friend_id))
        return friends


@graphql_object('Human')
@graphql_attr_field('home_planet', 'homePlanet', 'String')
class Human(Character):
    def __init__(
            self, character_id, name, appears_in, friend_ids, home_planet):
        super(Human, self).__init__(character_id, name, appears_in, friend_ids)
        self.home_planet = home_planet


@graphql_object('Droid')
@graphql_attr_field('primary_function', 'primaryFunction', 'String')
class Droid(Character):
    def __init__(
            self, character_id, name, appears_in, friend_ids,
            primary_function):
        super(Droid, self).__init__(character_id, name, appears_in, friend_ids)
        self.primary_function = primary_function


class Episode(object):
    A_NEW_HOPE = 4
    THE_EMPIRE_STRIKES_BACK = 5
    RETURN_OF_THE_JEDI = 6

    @staticmethod
    @graphql_enum('Episode')
    def graphql_episode_enum():
        return {
            'NEWHOPE': Episode.A_NEW_HOPE,
            'EMPIRE': Episode.THE_EMPIRE_STRIKES_BACK,
            'JEDI': Episode.RETURN_OF_THE_JEDI,
        }


class Heroes(object):
    @staticmethod
    @graphql_root_field('hero', 'Character', {'episode': 'Episode'})
    def hero(episode=None):
        if episode == Episode.THE_EMPIRE_STRIKES_BACK:
            return CharacterFactory.human('1000')
        else:
            return CharacterFactory.droid('2001')


class CharacterFactory(object):
    @staticmethod
    def character(character_id):
        ...

    @staticmethod
    @graphql_root_field('human', 'Human', {'id': 'String!'})
    def human(id):
        character = CharacterFactory.character(id)
        if isinstance(character, Human):
            return character
        else:
            return None

    @staticmethod
    @graphql_root_field('droid', 'Droid', {'id': 'String!'})
    def droid(id):
        character = CharacterFactory.character(id)
        if isinstance(character, Droid):
            return character
        else:
            return None
</pre>

# Setup
In order to execute a GraphQL document, we need to pass a `GraphQlContext` to
`GraphQlExecutor`.  The `GraphQlContext` contains the `GraphQlSchema`.  Here is
an example of how to obtain a `GraphQlSchema`:

<pre lang="python">
def schema_filename():
    """Return the name of the file that stores the schema."""
    return os.path.join(root_project_dir(), 'graphql_schema.json')


def generate_schema():
    """Compute the schema for the project and store it in schema_filename()."""
    # Find all of the modules in the project
    modules = []
    for dir_path, sub_dirs, sub_files in os.walk(root_project_dir()):
        for sub_file in sub_files:
            if sub_file.endswith('.py') and sub_file != '__init__.py':
                relative_filename = os.path.relpath(
                    os.path.join(dir_path, sub_file), root_project_dir())
                modules.append(relative_filename.replace(os.sep, '.')[:-3])

    # Create the GraphQlSchema
    schema = GraphQlSchemaFactory.create_from_modules(
        modules +
        # Include the standard implementations of the built-in scalar types
        ['graphql.scalar_descriptors.strict'])

    # Store the schema in schema_filename()
    with open(schema_filename(), 'w') as f:
        json.dump(schema.to_json(), f)


def get_schema():
    """Return the GraphQlSchema for the project."""
    with open(schema_filename(), 'r') as f:
        return GraphQlSchema.create_from_json(json.load(f))
</pre>

# Documentation
For more detailed instructions, check the source code to see the full API and
docstring documentation.
