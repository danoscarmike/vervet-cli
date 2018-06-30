from requests import exceptions


def handle_requests_error(function):
    def handle_requests_problems():
        try:
            function()
        except exceptions.Timeout:
            print('Timeout error making request to NuGet')
        except exceptions.TooManyRedirects:
            print('Bad URL: too many redirects')
        except exceptions.RequestException as e:
            print('This isn\'t good.')
            print(e)
    return handle_requests_problems
