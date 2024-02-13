class Rule:
    def __init__(self, classification: str, query: str) -> None:
        """
        Initialize the Rule class
        Args:
            classification (str): The classification of the rule
            query (str): The query to be executed
        """
        self.classification = classification
        self.query = query

        # TODO: Add query validation
        # TODO: Add potential classification validation (if we only want to allow certain classifications or if any
        #  classification should be optional)
