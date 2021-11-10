from euphonic import Spectrum1D, Quantity, ureg
from numpy import absolute, allclose, mean, square, sqrt


def diff_1d(spectrum: Spectrum1D,
            reference: Spectrum1D,
            fractional: bool = False,
            threshold: float = 1e-12) -> Quantity:
    """Compare the values of two Spectrum1D objects, returning an array

    Args:
        spectrum, reference: Spectra with same x-values for comparison
        fractional:
            Calculate relative difference by formula (S - R)/R. If False,
            use the unscaled difference between values instead.
        threshold:
            Ignore error from values smaller than this threshold in reference
            spectrum when fractional=True

    Returns:
        array Quantity:
            Difference between spectra
    """

    assert spectrum.x_data_unit == reference.x_data_unit
    assert allclose(spectrum.x_data.magnitude, reference.x_data.magnitude)

    diff = (spectrum.y_data.to(reference.y_data_unit).magnitude
            - reference.y_data.magnitude)

    if fractional:
        ref_values = reference.y_data.magnitude
        mask = absolute(ref_values) > threshold
        diff = diff[mask] / ref_values[mask] * ureg(None)

    else:
        diff *= spectrum.y_data.units

    return diff


def diff_1d_avg(spectrum: Spectrum1D,
                reference: Spectrum1D,
                fractional: bool = False,
                rms: bool = False,
                threshold: float = 1e-12) -> Quantity:
    """Compare the values of two Spectrum1D objects, returning a scalar

    Args:
        spectrum, reference: Spectra with same x-values for comparison
        fractional:
            Calculate relative difference by formula (S - R)/R. If False,
            use the unscaled difference between values instead.
        rms:
            Use root mean square to convert array to scalar. If False, use
            simple (signed) average.
        threshold:
            Ignore error from values smaller than this threshold in reference
            spectrum when fractional=True

    Returns:
        array Quantity:
            Average difference between spectra
    """

    diff = diff_1d(spectrum, reference,
                   fractional=fractional, threshold=threshold)

    if rms:
        return sqrt(mean(square(diff.magnitude))) * diff.units
    else:
        return mean(diff.magnitude) * diff.units
