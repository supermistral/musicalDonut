const mapObject = (obj, callback) => Object.fromEntries(
    Object.entries(obj).map(
        ([k, v], i) => [k, callback(v, k, i)]
));

export const translateClassNameToSelector = (className) => 
    "." + className;

export const translateClassObjToSelectors = (classObj) => 
    mapObject(classObj, translateClassNameToSelector);

