'use client';
import React from 'react';
import {useState, useEffect} from 'react';
import axios from 'axios';
import { openDatabase, addItem, getAllItems, getItemsByIds } from '../utils/indexedDB';
import styles from './page.module.css';

const Home = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [selectedName, setSelectedName] = useState('');
  const [loading, setLoading] = useState(false);
  const [items, setItems] = useState([]);
  const[existingNames, setExistingNames] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [uploading, setUploading] = useState(false);
  // Function to handle file input change

  useEffect(() => {
    fetchItems();
  }, []);

  const fetchItems = async () => {
    setLoading(true);
    try {
        await openDatabase(); 
        const allItems = await getAllItems();
        setItems(allItems);
        const names = allItems.map(item => item.name);
        setExistingNames(names);
    } catch (error) {
        console.error('Error fetching items from IndexedDB:', error);
    } finally {
        setLoading(false);
    }
  };

  const handleFileChange = (event) => {
    if(event.target.files[0]){
      setSelectedFile(event.target.files[0]);
      setSelectedName(event.target.files[0].name);
    }

  };

  const handleSearchChange = (event) =>{
    setSearchTerm(event.target.value);
  }

  const handleSearchSubmit = async(event) => {
    event.preventDefault();
    setLoading(true);
    const formData = new FormData();
    const allItems = await getAllItems();
    const allEmbeddings = allItems.map(item => item.embedding);
    const allIds = allItems.map(item => item.id);
    formData.append('embeddings', JSON.stringify(allEmbeddings));
    formData.append('searchTerm', searchTerm);
    formData.append('ids', JSON.stringify(allIds));

    try {
      const response = await axios.post('http://localhost:5000/findSimilar', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      if(response.data.length === 0){
        setItems([]);
      }
      else{
        const similarItems = await getItemsByIds(response.data);
        setItems(similarItems);
      }

      setLoading(false);
    } catch(error) {
      console.error("Error fetching similar images: ", error);
    }};

  // Function to handle form submission
  const handleSubmit = async (event) => {
    setUploading(true);
    event.preventDefault();
    if (!selectedFile) return;

    if (checkDuplicateName(selectedName)) {
      console.error('Duplicate name detected.');
      setUploading(false);
      return;
  }

    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('url', createImageUrl(selectedFile));
    formData.append('name', selectedName);

    try {
      const response = await axios.post('http://localhost:5000/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
    
      const imageObject = {
        name: selectedName,
        file: selectedFile,
        description: response.data['answer'],
        embedding: response.data['embedding']
    };
      console.log(response.data);

    await openDatabase(); 
    addItem(imageObject);
    setSelectedFile(null);
    setSelectedName('');
    fetchItems();
    setUploading(false);
    } catch (error) {
      console.error('Error uploading file:', error);
    }};

    const createImageUrl = (file) => {
      return URL.createObjectURL(file);
    };

    const checkDuplicateName = (name) => {
      return existingNames.includes(name);
  };

    return (
      <div className={styles.macPhotoApp}>
        
        <div className = {styles.headerContainer}>
          <form onSubmit={handleSubmit} className={styles.searchForm}>
              <button type="submit" className={styles.btnPrimary}>
                  Upload
              </button>
              <div>
                <label htmlFor="fileInput"> </label>
                  <input
                      type="file"
                      className={styles.formControlFile}
                      id="fileInput"
                      onChange={handleFileChange}
                  />
              </div>

          </form>
          <form onSubmit={handleSearchSubmit}  className = {styles.searchForm}>
              <input
                  type="text"
                  value={searchTerm}
                  onChange={handleSearchChange}
                  placeholder="Search..."
                  className={styles.inputSearch}
              />
              <button type="submit" className={styles.btnSearch}>
                Search
              </button>
          </form>
        </div>
        {uploading? (
            <h4> uploading...</h4>
        ) : (
          <h2 style={{ display: 'none' }}> </h2>
        )
      }
         
          {loading ? (
              <div className={styles.loading}>Loading...</div>
          ) : (
            items.length === 0 ? (
              <div className = {styles.loading}> No items found </div>
            ) : (
              <div className={styles.imageGrid}>
                  {items.map(item => (
                      <div key={item.id} className={styles.imageItem}>
                          <img src={createImageUrl(item.file)} alt={item.name} className={styles.image} />
                      </div>
                  ))}
              </div>
          ))}
      </div>
  );

};

export default Home;

