import subprocess

from cmake_language_server.api import API


def test_query_with_cache(cmake_build):
    api = API('cmake', cmake_build)
    assert api.query()

    query = cmake_build / '.cmake' / 'api' / 'v1' / 'query'
    assert query.exists()

    reply = cmake_build / '.cmake' / 'api' / 'v1' / 'reply'
    assert reply.exists()


def test_query_without_cache(cmake_build):
    api = API('cmake', cmake_build)
    (cmake_build / 'CMakeCache.txt').unlink()

    assert not api.query()


def test_read_variable(cmake_build):
    api = API('cmake', cmake_build)
    assert api.query()
    assert api.read_reply()

    assert api.get_variable_doc('testproject_BINARY_DIR')


def test_read_cmake_files(cmake_build):
    api = API('cmake', cmake_build)
    api.parse_doc()
    assert api.query()
    api.read_reply()

    assert 'GNU' in api.get_variable_doc('CMAKE_CXX_COMPILER_ID')


def test_parse_commands(cmake_build):
    api = API('cmake', cmake_build)
    api.parse_doc()

    p = subprocess.run(['cmake', '--help-command-list'],
                       universal_newlines=True,
                       stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE)
    commands = p.stdout.strip().split('\n')

    for command in commands:
        assert api.get_command_doc(command) is not None, f'{command} not found'

    assert 'break()' in api.get_command_doc('break')
    assert api.get_command_doc('not_existing_command') is None


def test_parse_variables(cmake_build):
    api = API('cmake', cmake_build)
    api.parse_doc()

    p = subprocess.run(['cmake', '--help-variable-list'],
                       universal_newlines=True,
                       stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE)
    variables = p.stdout.strip().split('\n')

    for variable in variables:
        if '<' in variable:
            continue
        assert api.get_variable_doc(
            variable) is not None, f'{variable} not found'

    assert api.get_variable_doc('BUILD_SHARED_LIBS') is not None
    assert api.get_variable_doc('not_existing_variable') is None