def all_params_perms(params):
    if len(params) <=1:
        return map(lambda x: [x], params[0])
    else:
        all_perms = []
        for v in params[0]:
            for perm in all_params_perms(params[1:]):
                np = [v] + perm
                all_perms.append(np)
        return all_perms


pp = all_params_perms([[0,0.5,1],[0,0.2,0.4,0.6,0.8,1]])
print pp