import logging
import collections


class Document:
    # Sets up the conenction to the specified document
    def __init__(self, connection, document_name):
        self.db = connection[document_name]
        self.logger = logging.getLogger(__name__)

    # <-- Pointer Methods -->
    # For simpler calls, points to self.update_by_id
    async def update(self, dict):
        await self.update_by_id(dict)

    # This is essentially find_by_id so point to that
    async def get_by_id(self, id):
        return await self.find_by_id(id)

    # For simpler calls, points to self.find_by_id
    async def find(self, id):
        return await self.find_by_id(id)

    # For simpler calls, points to self.delete_by_id
    async def delete(self, id):
        await self.delete_by_id(id)

    # <-- Actual Methods -->
    # Returns the data found under `id`
    async def find_by_id(self, id):
        return await self.db.find_one({"_id": id})

    # Deletes all items found with _id: `id`
    async def delete_by_id(self, id):
        if not await self.find_by_id(id):
            return

        await self.db.delete_many({"_id": id})

    # Insert something into the db
    async def insert(self, dict):
        # Check if its actually a Dictionary
        if not isinstance(dict, collections.abc.Mapping):
            raise TypeError("Expected Dictionary.")
        # Always use your own _id
        if not dict["_id"]:
            raise KeyError("_id not found in supplied dict.")

        await self.db.insert_one(dict)

    # Makes a new item in the document, if it already exists it will update that item instead
    # This function parses an input Dictionary to get the relevant information needed to insert
    async def upsert(self, dict):
        if await self.__get_raw(dict["_id"]) != None:
            await self.update_by_id(dict)
        else:
            await self.db.insert_one(dict)

    # For when a document already exists in the data and you want to update something in it
    # This function parses an input Dictionary to get the relevant information needed to update
    async def update_by_id(self, dict):
        # Check if its actually a Dictionary
        if not isinstance(dict, collections.abc.Mapping):
            raise TypeError("Expected Dictionary.")

        # Always use your own _id
        if not dict["_id"]:
            raise KeyError("_id not found in supplied dict.")

        if not await self.find_by_id(dict["_id"]):
            return

        id = dict["_id"]
        dict.pop("_id")
        await self.db.update_one({"_id": id}, {"$set": dict})

    # For when you want to remove a field from a pre-existing document in the collection
    # This function parses an input Dictionary to get the relevant information needed to unset
    async def unset(self, dict):
        # Check if its actually a Dictionary
        if not isinstance(dict, collections.abc.Mapping):
            raise TypeError("Expected Dictionary.")

        # Always use your own _id
        if not dict["_id"]:
            raise KeyError("_id not found in supplied dict.")

        if not await self.find_by_id(dict["_id"]):
            return

        id = dict["_id"]
        dict.pop("_id")
        await self.db.update_one({"_id": id}, {"$unset": dict})

    # Increment a given `field` by `amount`
    async def increment(self, id, amount, field):
        if not await self.find_by_id(id):
            return

        await self.db.update_one({"_id": id}, {"$inc": {field: amount}})

    # Returns a list of all data in the document
    async def get_all(self):
        data = []
        async for document in self.db.find({}):
            data.append(document)
        return data

    # An internal private method used to eval certain checks within other methods which require the actual data
    # <-- Private methods -->
    async def __get_raw(self, id):
        return await self.db.find_one({"_id": id})