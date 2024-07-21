const DB_NAME = 'userImagesDatabase';
const DB_VERSION = 1;
let db;

const openDatabase = () => {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open(DB_NAME, DB_VERSION);
        request.onerror = (event) => {
            console.error('Error opening database:', event.target.error);
            reject(event.target.error);
        };

        request.onsuccess = (event) => {
            db = event.target.result;
            resolve(db);
        };

        request.onupgradeneeded = (event) => {
            const db = event.target.result;
            db.createObjectStore('images', { keyPath: 'id', autoIncrement: true });
        };
    });
};

const addItem = (item) => {
    const transaction = db.transaction(['images'], 'readwrite');
    const store = transaction.objectStore('images');
    store.add(item);
};

const getAllItems = () => {
    const transaction = db.transaction(['images'], 'readonly');
    const store = transaction.objectStore('images');
    const request = store.getAll();

    return new Promise((resolve, reject) => {
        request.onsuccess = (event) => {
            resolve(event.target.result);
        };

        request.onerror = (event) => {
            reject(event.target.error);
        };
    });
};

const getItemsByIds = (ids) => {
    const transaction = db.transaction(['images'], 'readonly');
    const store = transaction.objectStore('images');

    return new Promise((resolve, reject) => {
        const items = [];
        let count = ids.length;

        ids.forEach(id => {
            const request = store.get(id);
            
            request.onsuccess = (event) => {
                items.push(event.target.result);
                count--;

                if (count === 0) {
                    resolve(items);
                }
            };

            request.onerror = (event) => {
                reject(event.target.error);
            };
        });
    });
};

export { openDatabase, addItem, getAllItems, getItemsByIds };