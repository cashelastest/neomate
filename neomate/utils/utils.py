
def query_maker(kwargs:dict)->str:
    """Generates Cypher query parameters string from dictionary.

        Handles different value types:
        - Strings are wrapped in single quotes
        - Numbers and other types are converted to string as-is

        Args:
            kwargs (dict): Dictionary of parameter names and values

        Returns:
            str: Formatted string ready for Cypher query:
                "key1:'value1',key2:123,..."
        """
    return ",".join(map(
                    lambda x:f"""{x[0]}:'{x[1]}'""" if isinstance(x[1],str) else f"{x[0]}:{x[1]}",
                    kwargs.items()
                ))