class MultiDict(dict):
    def __setitem__(self, key, value):
        try:
            current_value = super().__getitem__(key)
        except KeyError:
            current_value = None

        if current_value is not None:
            if isinstance(current_value, tuple):
                # if we're already storing multiple values
                current_value = list(current_value)
                new_value = current_value.append(value)
                new_value = tuple(new_value) # immutability
                super().__setitem__(key, new_value)
            else:
                new_value = (current_value, value)
                super().__setitem__(key, new_value)
        else:
            super().__setitem__(key, value)

        return None

class CaseInsensitiveMultiDict(MultiDict):
    def __setitem__(self, key: str, value):
        if not isinstance(key, str):
            raise ValueError(
                "Keys being passed to CaseInsensitiveMultiDict must be of type 'str', not {}", key.__class__.__name__
            )
        key = key.lower()
        return super().__setitem__(key, value)

    def __getitem__(self, key: str):
        if not isinstance(key, str):
            raise ValueError(
                "Keys being passed to CaseInsensitiveMultiDict [search] must be of type 'str', not {}", key.__class__.__name__
            )

        return super().__getitem__(key.lower())