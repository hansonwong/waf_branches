import ctypes, ctypes.util, threading
libpthread_path = ctypes.util.find_library("pthread")
if libpthread_path:
    libpthread = ctypes.CDLL(libpthread_path)
    if hasattr(libpthread, "pthread_setname_np"):
        pthread_setname_np = libpthread.pthread_setname_np
        pthread_setname_np.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
        pthread_setname_np.restype = ctypes.c_int
        orig_start = threading.Thread.start
        def new_start(self):
            orig_start(self)
            try:
                name = "bvsd_%s" % self.name
                if not name or name.startswith('Thread-'):
                    name = self.__class__.__name__
                    if name == 'Thread':
                        name = self.name
                if name:
                    if isinstance(name, unicode):
                        name = name.encode('ascii', 'replace')
                    ident = getattr(self, "ident", None)
                    if ident is not None:
                        pthread_setname_np(ident, name[:15])
            except Exception:
                pass  # Don't care about failure to set name
        threading.Thread.start = new_start
