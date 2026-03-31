import logging

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

class UomConverter:
    """
    Helper class to convert raw VersaTrak sensor readings to human-readable units.
    """

    def __init__(self, uom_data):
        """
        Initialize with UOM metadata.
        uom_data can be a dictionary mapping UOM IDs to their metadata.
        """
        self.uom_map = uom_data

    def convert(self, value, uom_id):
        """
        Convert a raw value to the units specified by uom_id.
        Returns the converted float value.
        """
        if uom_id not in self.uom_map:
            logger.warning(
                f"UOM ID {uom_id} not found in metadata. Returning raw value."
            )
            return value

        uom = self.uom_map[uom_id]

        s1 = uom.get("dispS1", 1.0)
        o1 = uom.get("dispO1", 0.0)
        s2 = uom.get("dispS2", 1.0)
        o2 = uom.get("dispO2", 0.0)

        # Formula: (v * s1 + o1) * s2 + o2
        converted = (value * s1 + o1) * s2 + o2
        return converted

    def format(self, value, uom_id):
        """
        Convert and format a raw value as a string with units and proper decimal places.
        """
        if uom_id not in self.uom_map:
            return f"{value}"

        uom = self.uom_map[uom_id]
        converted = self.convert(value, uom_id)

        decimals = uom.get("nDec", 1)
        units = uom.get("dispUom", "")

        return f"{converted:.{decimals}f} {units}".strip()

    def convert_series(self, series, uom_id):
        """
        Convert a pandas Series of raw values to the units specified by uom_id.
        """
        if uom_id not in self.uom_map:
            logger.warning(
                f"UOM ID {uom_id} not found in metadata. Returning raw series."
            )
            return series

        uom = self.uom_map[uom_id]

        s1 = uom.get("dispS1", 1.0)
        o1 = uom.get("dispO1", 0.0)
        s2 = uom.get("dispS2", 1.0)
        o2 = uom.get("dispO2", 0.0)

        # Formula: (v * s1 + o1) * s2 + o2
        return (series * s1 + o1) * s2 + o2
