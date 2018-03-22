import tensorflow as tf
import numpy as np
from functools import wraps

def figure_buffer(fig):
    '''Extract raw image buffer from matplotlib figure shaped as 1xHxWx3.'''  
    fig.canvas.draw()  
    buf = fig.canvas.tostring_rgb()
    w, h = fig.canvas.get_width_height()
    return np.fromstring(buf, dtype=np.uint8).reshape((1, h, w, 3))

def figure_summary(name, *tf_image_args, **tf_image_kwargs):
    '''Transforms functions returning matplotlib figures into tf.summary.images.

    This is a convenience to transform matplotlib figures into tf.summary images,
    which can then be written into standard tensorflow summary format and visualized
    in tensorboard. Intended usage:

        import tfmpl

        @tfmpl.figure_summary(name='myimage')
        def my_draw(points):            
            fig, ax = plt.subplots()
            ax.scatter(points[:, 0], points[:, 1], c='r')
            return fig

        img_summary = my_draw(points_tensor)
        all_summaries = tf.summary.merge_all()

    In the above example, points_tensor is a tensorflow tensor that is required for drawing
    our custom figure. `mpl_image_summary` ensures that dependencies on tensors are evaluated
    before invoking the drawing function. The result of these dependencies will be given as
    numpy arrays into drawing routine (see tf.py_func for details).

    Params
    ------
    name : string-like
        Name of resulting image summary    
    tf_image_args : array-like, optional
        Additional arguments to be passed to tf.summary.image

    Kwargs
    ------
    tf_image_kwargs : dict-like, optional
        Additional keyword arguments to be passed to tf.summary.image
    '''
    def decorator(func):
        @wraps(func)
        def wrapper(*tf_pyfnc_args, **tf_pyfnc_kwargs):
            genfnc = lambda *args, **kwargs : figure_buffer(func(*args, **kwargs))
            image_tensor = tf.py_func(genfnc, tf_pyfnc_args, tf.uint8, **tf_pyfnc_kwargs)
            return tf.summary.image(name, image_tensor, *tf_image_args, **tf_image_kwargs)
        return wrapper
    return decorator
