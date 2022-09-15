# Queries

## Single result queries
1. total credentials used
    ```js
        db.credentials.countDocuments({'used': {'$ne': null}})
    ```

2. total credentials used for a particular service
    - replace `ObjectId` with `ObjectId` of desired service.
    ```js
    db.credentials.countDocuments({'used': {'$ne': null}, 'service_id':  ObjectId('631f6487a38643854c67180c')})
    ```

3. total credentials used by a particular user
    - replace `ObjectId` with `ObjectId` of desired user.
    ```js
    db.credentials.countDocuments({'used': {'$ne': null}, 'used.by':  ObjectId('631f636ba38643854c67180b')})
    ```

## Multiple result queries
1. total credentials used per service
    - save as aggregation pipeline.
    ```js
    [
        {
            $match: {
                used: {
                    $ne: null
                }
            }
        },
        {
            $group: {
                _id: '$service_id',
                count: {
                    $count: {}
                }
            }
        },
        {
            $lookup: {
                from: 'services',
                localField: '_id',
                foreignField: '_id',
                as: 'services'
            }
        },
        {
            $unwind: '$services'
        },
        {
            $set: {
                service_name: '$services.name'
            }
        },
        {
            $unset: [
                '_id',
                'services'
            ]
        }
    ]
    ```

2. total credentials used per user
    - save as aggregation pipeline.
    ```js
    [
        {
            $match: {
                used: {
                    $ne: null
                }
            }
        },
        {
            $group: {
                _id: '$used.by',
                count: {
                    $count: {}
                }
            }
        },
        {
            $lookup: {
                from: 'users',
                localField: '_id',
                foreignField: '_id',
                as: 'users'
            }
        },
        {
            $unwind: '$users'
        },
        {
            $set: {
                user: {
                    username: '$users.username',
                    first_name: '$users.first_name',
                    last_name: '$users.last_name'
                }
            }
        },
        {
            $unset: [
                '_id',
                'users'
            ]
        }
    ]
    ```

3. total credentials used per user per service
    - save as aggregation pipeline.
    ```js
    [
        {
            $match: {
                used: {
                    $ne: null
                }
            }
        },
        {
            $group: {
                _id: {
                    service_id: '$service_id',
                    user_id: '$used.by'
                },
                count: {
                    $count: {}
                }
            }
        },
        {
            $lookup: {
                from: 'services',
                localField: '_id.service_id',
                foreignField: '_id',
                as: 'services'
            }
        },
        {
            $lookup: {
                from: 'users',
                localField: '_id.user_id',
                foreignField: '_id',
                as: 'users'
            }
        },
        {
            $unwind: '$services'
        },
        {
            $unwind: '$users'
        },
        {
            $set: {
                service_name: '$services.name',
                user: {
                    username: '$users.username',
                    first_name: '$users.first_name',
                    last_name: '$users.last_name'
                }
            }
        },
        {
            $unset: [
                '_id',
                'services',
                'users'
            ]
        }
    ]
    ```

## Advanced filtering
1. filtering based on date or date range
    - modify the _query_ from `{used: {$ne: null}}` to instead filter using date as show:
    ```js
    {
        'used.at': {
            '$gte': ISODate('2022-09-12T00:00:00'),
            '$lt': ISODate('2022-09-13T00:00:00')
        }
    }
    ```
    - This example will include those records where credentials were used on the date `2022-09-12` i.e, _12th September 2022_.
    - Similarly we can also filter a range of dates, like so:
    ```js
    {
        'used.at': {
            '$gte': ISODate('2022-09-12T00:00:00'),
            '$lt': ISODate('2022-09-15T00:00:00')
        }
    }
    ```
    - This example will include those records where credentials were used between the dates `2022-09-12`(**inclusive**) and `2022-09-15`(**exclusive**). So, only records fetched on _12th, 13th or 14th of September 2022_ will be included.
