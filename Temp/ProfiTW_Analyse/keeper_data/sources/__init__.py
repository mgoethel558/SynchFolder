"""Datenquellen-Adapter (Adapter-Pattern, §8).

Jeder Adapter implementiert :class:`~keeper_data.sources.base.SourceAdapter`
und liefert eine Liste roher :class:`RawRecord`. Die Normalisierung inkl.
GK-Filter passiert zentral in ``keeper_data.normalize``.
"""
