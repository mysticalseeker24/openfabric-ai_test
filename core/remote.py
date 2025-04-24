from typing import Optional, Union

# Local implementations of Proxy and ExecutionResult

class ExecutionResult:
    """
    Simulates the ExecutionResult class from the Openfabric SDK.
    Represents the result of an asynchronous execution request.
    """
    
    def __init__(self, data=None, status='completed'):
        self._data = data
        self._status = status
    
    def wait(self):
        """Simulate waiting for asynchronous operation"""
        pass
    
    def status(self):
        """Return the status of the execution"""
        return self._status
    
    def data(self):
        """Return the result data"""
        return self._data


class Proxy:
    """
    Simulates the Proxy class from the Openfabric SDK.
    Handles communication with remote Openfabric services.
    """
    
    def __init__(self, proxy_url, proxy_tag=None, ssl_verify=True):
        self.proxy_url = proxy_url
        self.proxy_tag = proxy_tag
        self.ssl_verify = ssl_verify
    
    def request(self, inputs, uid):
        """
        Simulate an asynchronous request to a service.
        
        Args:
            inputs (dict): Input data for the request
            uid (str): User ID making the request
        
        Returns:
            ExecutionResult: A result object
        """
        # This is a mock implementation - in a real environment, this would actually 
        # send a request to the service and return the pending result
        return ExecutionResult({"message": "Operation simulated"})
    
    def execute(self, inputs, configs, uid):
        """
        Simulate a synchronous request to a service.
        
        Args:
            inputs (dict): Input data for the request
            configs (dict): Configuration parameters
            uid (str): User ID making the request
        
        Returns:
            ExecutionResult: A result object with completed status
        """
        # This is a mock implementation - in a real environment, this would 
        # perform a synchronous request and wait for the result
        return ExecutionResult({"message": "Operation simulated"})


class Remote:
    """
    Remote is a helper class that interfaces with an Openfabric Proxy instance
    to send input data, execute computations, and fetch results synchronously
    or asynchronously.

    Attributes:
        proxy_url (str): The URL to the proxy service.
        proxy_tag (Optional[str]): An optional tag to identify a specific proxy instance.
        client (Optional[Proxy]): The initialized proxy client instance.
    """

    # ----------------------------------------------------------------------
    def __init__(self, proxy_url: str, proxy_tag: Optional[str] = None):
        """
        Initializes the Remote instance with the proxy URL and optional tag.

        Args:
            proxy_url (str): The base URL of the proxy.
            proxy_tag (Optional[str]): An optional tag for the proxy instance.
        """
        self.proxy_url = proxy_url
        self.proxy_tag = proxy_tag
        self.client: Optional[Proxy] = None

    # ----------------------------------------------------------------------
    def connect(self) -> 'Remote':
        """
        Establishes a connection with the proxy by instantiating the Proxy client.

        Returns:
            Remote: The current instance for chaining.
        """
        self.client = Proxy(self.proxy_url, self.proxy_tag, ssl_verify=False)
        return self

    # ----------------------------------------------------------------------
    def execute(self, inputs: dict, uid: str) -> Union[ExecutionResult, None]:
        """
        Executes an asynchronous request using the proxy client.

        Args:
            inputs (dict): The input payload to send to the proxy.
            uid (str): A unique identifier for the request.

        Returns:
            Union[ExecutionResult, None]: The result of the execution, or None if not connected.
        """
        if self.client is None:
            return None

        return self.client.request(inputs, uid)

    # ----------------------------------------------------------------------
    @staticmethod
    def get_response(output: ExecutionResult) -> Union[dict, None]:
        """
        Waits for the result and processes the output.

        Args:
            output (ExecutionResult): The result returned from a proxy request.

        Returns:
            Union[dict, None]: The response data if successful, None otherwise.

        Raises:
            Exception: If the request failed or was cancelled.
        """
        if output is None:
            return None

        output.wait()
        status = str(output.status()).lower()
        if status == "completed":
            return output.data()
        if status in ("cancelled", "failed"):
            raise Exception("The request to the proxy app failed or was cancelled!")
        return None

    # ----------------------------------------------------------------------
    def execute_sync(self, inputs: dict, configs: dict, uid: str) -> Union[dict, None]:
        """
        Executes a synchronous request with configuration parameters.

        Args:
            inputs (dict): The input payload.
            configs (dict): Additional configuration parameters.
            uid (str): A unique identifier for the request.

        Returns:
            Union[dict, None]: The processed response, or None if not connected.
        """
        if self.client is None:
            return None

        output = self.client.execute(inputs, configs, uid)
        return Remote.get_response(output)
