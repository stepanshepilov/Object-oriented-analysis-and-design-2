import React, { useState, useEffect } from 'react';
import api from './api'; // Твой axios конфиг
import { ShoppingCart, Plus, Package, Search } from 'lucide-react';

function App() {
  const [products, setProducts] = useState([]);
  const [view, setView] = useState('shop'); 
  const [newProduct, setNewProduct] = useState({ name: '', price: 0, stock: 0 });

  // 1. Загрузка данных из твоего Java API
  const fetchProducts = async () => {
    try {
      const response = await api.get('/products');
      setProducts(response.data);
    } catch (error) {
      console.error("Бэкенд не отвечает:", error);
    }
  };

  useEffect(() => {
    fetchProducts();
  }, []);

  // 2. Оформление заказа через API
  const handleOrder = async (productName) => {
    try {
      const res = await api.post('/order', { productName, quantity: 1 });
      alert(res.data);
      fetchProducts(); // Обновляем список, чтобы увидеть новый остаток
    } catch (error) {
      alert("Ошибка при связи с сервером");
    }
  };

  // 3. Добавление товара через API (Админка)
  const handleAddProduct = async (e) => {
    e.preventDefault();
    try {
      await api.post('/admin/add', newProduct);
      alert("Товар успешно добавлен в БД!");
      setNewProduct({ name: '', price: 0, stock: 0 });
      fetchProducts();
      setView('shop');
    } catch (error) {
      alert("Ошибка при добавлении");
    }
  };

  return (
    <div className="min-h-screen font-sans bg-[#f6f6f6]">
      {/* HEADER */}
      <header className="bg-[#ff6700] text-white p-4 shadow-md sticky top-0 z-50">
        <div className="container mx-auto flex justify-between items-center gap-4">
          <div 
            className="text-3xl font-black cursor-pointer select-none" 
            onClick={() => setView('shop')}
          >
            DNS
          </div>
          
          <div className="flex-1 max-w-2xl relative">
            <input 
              type="text" 
              placeholder="Поиск по категориям и товарам" 
              className="w-full p-2 pl-4 rounded text-black outline-none focus:shadow-inner"
            />
            <Search className="absolute right-3 top-2 text-gray-400" size={20} />
          </div>

          <div className="flex items-center gap-6">
            <button 
              onClick={() => setView('admin')} 
              className="hover:bg-orange-600 px-3 py-2 rounded transition-colors flex items-center gap-2"
            >
              <Package size={20}/> Админка
            </button>
            <div className="relative cursor-pointer hover:bg-orange-600 p-2 rounded-full transition-colors">
              <ShoppingCart size={28} />
            </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto p-6">
        {view === 'shop' ? (
          <>
            <h1 className="text-2xl font-bold mb-6 text-gray-800">Каталог</h1>
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6">
              {products.map((product, idx) => (
                <div 
                  key={idx} 
                  className="bg-white p-4 rounded-lg shadow-sm hover:shadow-lg transition-shadow border border-transparent hover:border-orange-200 flex flex-col justify-between h-full"
                >
                  <div>
                    {/* КАРТИНКА ГРУЗИТСЯ ИЗ ПАПКИ PUBLIC/MEDIA */}
                    <div className="h-40 w-full mb-4 flex items-center justify-center overflow-hidden bg-white">
                      <img 
                        src={`/${product.name}.png`} 
                        alt={product.name} 
                        className="max-h-full max-w-full object-contain hover:scale-110 transition-transform duration-300"
                        onError={(e) => {
                          e.target.onerror = null; 
                          e.target.src = "https://placehold.co/200x150?text=Нет+фото";
                        }}
                      />
                    </div>
                    <h2 className="text-sm font-medium leading-snug mb-2 text-gray-700 hover:text-blue-600 cursor-pointer h-10 overflow-hidden">
                      {product.name}
                    </h2>
                  </div>

                  <div className="mt-4">
                    <div className="text-2xl font-extrabold mb-1">
                      {product.price.toLocaleString()} ₽
                    </div>
                    <div className={`text-[11px] mb-3 font-bold uppercase ${product.stock > 0 ? 'text-green-600' : 'text-red-500'}`}>
                      {product.stock > 0 ? `В наличии: ${product.stock}` : 'Срок поставки: уточнить'}
                    </div>
                    <button 
                      onClick={() => handleOrder(product.name)}
                      disabled={product.stock <= 0}
                      className={`w-full py-2 rounded font-bold transition-all ${
                        product.stock > 0 
                        ? 'bg-[#ff6700] text-white hover:bg-[#e65c00]' 
                        : 'bg-gray-200 text-gray-400 cursor-not-allowed'
                      }`}
                    >
                      Купить
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </>
        ) : (
          /* АДМИН-ПАНЕЛЬ */
          <div className="max-w-md mx-auto bg-white p-8 rounded-lg shadow-xl">
            <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
              <Plus className="text-orange-500" /> Новый товар (Бэкенд)
            </h2>
            <form onSubmit={handleAddProduct} className="space-y-4">
              <div>
                <label className="block text-sm font-bold text-gray-600 mb-1">Название товара</label>
                <input 
                  type="text" 
                  required
                  className="w-full border border-gray-300 rounded p-2 focus:border-orange-500 outline-none"
                  value={newProduct.name}
                  onChange={(e) => setNewProduct({...newProduct, name: e.target.value})}
                />
              </div>
              <div>
                <label className="block text-sm font-bold text-gray-600 mb-1">Цена (₽)</label>
                <input 
                  type="number" 
                  required
                  className="w-full border border-gray-300 rounded p-2 focus:border-orange-500 outline-none"
                  value={newProduct.price}
                  onChange={(e) => setNewProduct({...newProduct, price: parseFloat(e.target.value)})}
                />
              </div>
              <div>
                <label className="block text-sm font-bold text-gray-600 mb-1">Количество</label>
                <input 
                  type="number" 
                  required
                  className="w-full border border-gray-300 rounded p-2 focus:border-orange-500 outline-none"
                  value={newProduct.stock}
                  onChange={(e) => setNewProduct({...newProduct, stock: parseInt(e.target.value)})}
                />
              </div>
              <div className="flex gap-3 pt-4">
                <button type="submit" className="flex-1 bg-green-600 text-white py-2 rounded font-bold hover:bg-green-700">
                  Сохранить в БД
                </button>
                <button type="button" onClick={() => setView('shop')} className="flex-1 bg-gray-100 py-2 rounded">
                  Отмена
                </button>
              </div>
            </form>
          </div>
        )}
      </main>

      <footer className="mt-20 bg-[#333] text-gray-400 py-10 px-4">
        <div className="container mx-auto text-center">
          <p className="text-sm">© 2024 DNS Клон. Работает через Java API на порту 8080.</p>
        </div>
      </footer>
    </div>
  );
}

export default App;