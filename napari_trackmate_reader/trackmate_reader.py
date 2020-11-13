from napari_plugin_engine import napari_hook_implementation
from pytrackmate import trackmate_peak_import


@napari_hook_implementation
def napari_get_reader(path):
    """A basic implementation of the napari_get_reader hook specification.

    Parameters
    ----------
    path : str or list of str
        Path to file, or list of paths.

    Returns
    -------
    function or None
        If the path is a recognized format, return a function that accepts the
        same path or list of paths, and returns a list of layer data tuples.
    """
    if isinstance(path, list):
        # reader plugins may be handed single path, or a list of paths.
        # if it is a list, it is assumed to be an image stack...
        # so we are only going to look at the first file.
        path = path[0]

    # if we know we cannot read the file, we immediately return None.
    extensions = ".xml",
    if not path.endswith(extensions):
        return None

    # otherwise we return the *function* that can read ``path``.
    return reader_function


def reader_function(path):
    """Take a path or list of paths and return a list of LayerData tuples.

    Readers are expected to return data as a list of tuples, where each tuple
    is (data, [add_kwargs, [layer_type]]), "add_kwargs" and "layer_type" are
    both optional.

    Parameters
    ----------
    path : str or list of str
        Path to file, or list of paths.

    Returns
    -------
    layer_data : list of tuples
        A list of LayerData tuples where each tuple in the list contains
        (data, metadata, layer_type), where data is a numpy array, metadata is
        a dict of keyword arguments for the corresponding viewer.add_* method
        in napari, and layer_type is a lower-case string naming the type of layer.
        Both "meta", and "layer_type" are optional. napari will default to
        layer_type=="image" if not provided
    """
    # handle both a string and a list of strings
    paths = [path] if isinstance(path, str) else path

    layer_data = []
    for _path in paths:
        # load all files into array
        peaks = trackmate_peak_import(_path, get_tracks=True).reset_index(drop=True)
        sorted_peaks = peaks.sort_values(['label', 't'], ignore_index=True)

        # extract the data, properties
        data = sorted_peaks.loc[:, ('label', 't', 'y', 'x')]

        # TODO(arl): extract the graph information

        # optional kwargs for the corresponding viewer.add_* method
        # https://napari.org/docs/api/napari.components.html#module-napari.components.add_layers_mixin
        add_kwargs = {'properties': sorted_peaks}
        layer_type = "tracks"  # optional, default is "image"
        layer_data.append((data, add_kwargs, layer_type))

    return layer_data
