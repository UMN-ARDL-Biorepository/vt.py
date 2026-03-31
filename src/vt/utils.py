import logging

logger = logging.getLogger(__name__)


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
        self.name_map = {}
        for uom_id, metadata in uom_data.items():
            name = metadata.get("name")
            display_name = metadata.get("dispUom")
            if name:
                self.name_map[name.lower()] = uom_id
            if display_name:
                self.name_map[display_name.lower()] = uom_id

    def _resolve_uom_id(self, uom_reference):
        """
        Resolve a UOM reference (ID or name/display unit) to a UOM ID.
        """
        if uom_reference in self.uom_map:
            return uom_reference
        return self.name_map.get(str(uom_reference).lower())

    def convert(self, value, uom_reference):
        """
        Convert a raw value to the units specified by UOM ID or name.
        Returns the converted float value.
        """
        uom_id = self._resolve_uom_id(uom_reference)
        if not uom_id:
            logger.warning(
                f"UOM '{uom_reference}' not found in metadata. Returning raw value."
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

    def format(self, value, uom_reference):
        """
        Convert and format a raw value as a string with units and proper decimal places.
        """
        uom_id = self._resolve_uom_id(uom_reference)
        if not uom_id:
            return f"{value}"

        uom = self.uom_map[uom_id]
        converted = self.convert(value, uom_id)
        decimals = uom.get("nDec", 1)
        units = uom.get("dispUom", "")

        return f"{converted:.{decimals}f} {units}".strip()

    def convert_series(self, series, uom_reference):
        """
        Convert a pandas Series of raw values to the units specified by UOM ID or name.
        """
        uom_id = self._resolve_uom_id(uom_reference)
        if not uom_id:
            logger.warning(
                f"UOM '{uom_reference}' not found in metadata. Returning raw series."
            )
            return series

        uom = self.uom_map[uom_id]

        s1 = uom.get("dispS1", 1.0)
        o1 = uom.get("dispO1", 0.0)
        s2 = uom.get("dispS2", 1.0)
        o2 = uom.get("dispO2", 0.0)

        # Formula: (v * s1 + o1) * s2 + o2
        return (series * s1 + o1) * s2 + o2
