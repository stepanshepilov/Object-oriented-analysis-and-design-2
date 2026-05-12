import React, { useState, useEffect } from 'react';
import api from './api'; 
import { ShoppingCart, Plus, Package, Search, X, Trash2 } from 'lucide-react';

function App() {
  const [products, setProducts] = useState([]);
  const [view, setView] = useState('shop'); 
  const [newProduct, setNewProduct] = useState({ name: '', price: 0, stock: 0 });
  
  // --- НОВЫЕ СОСТОЯНИЯ ---
  const [searchQuery, setSearchQuery] = useState(''); // Для поиска
  const [cart, setCart] = useState([]); // Для корзины
  const [isCartOpen, setIsCartOpen] = useState(false); // Показ модалки корзины

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

  // --- ЛОГИКА ПОИСКА (ФИЛЬТРАЦИЯ) ---
  const filteredProducts = products.filter(p => 
    p.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // --- ЛОГИКА КОРЗИНЫ ---
  const addToCart = (product) => {
    setCart(prev => {
      const existing = prev.find(item => item.name === product.name);
      if (existing) return prev.map(item => item.name === product.name ? {...item, count: item.count + 1} : item);
      return [...prev, { ...product, count: 1 }];
    });
  };

  const removeFromCart = (name) => {
    setCart(prev => prev.filter(item => item.name !== name));
  };

  const handleCheckout = async () => {
    try {
      for (const item of cart) {
        await api.post('/order', { productName: item.name, quantity: item.count });
      }
      alert("Все заказы из корзины оформлены!");
      setCart([]);
      setIsCartOpen(false);
      fetchProducts();
    } catch (error) {
      alert("Ошибка при оформлении части заказов");
    }
  };

  const handleAddProduct = async (e) => {
    e.preventDefault();
    try {
      await api.post('/admin/add', newProduct);
      alert("Товар добавлен!");
      setNewProduct({ name: '', price: 0, stock: 0 });
      fetchProducts();
      setView('shop');
    } catch (error) {
      alert("Ошибка при добавлении");
    }
  };

  return (
    <div className="min-h-screen font-sans bg-[#f6f6f6] relative">
      {/* HEADER */}
      <header className="bg-[#ff6700] text-white p-4 shadow-md sticky top-0 z-50">
        <div className="container mx-auto flex justify-between items-center gap-4">
          <div className="text-3xl font-black cursor-pointer" onClick={() => setView('shop')}>DNS</div>
          
          {/* ИНПУТ ПОИСКА */}
          <div className="flex-1 max-w-2xl relative">
            <input 
              type="text" 
              placeholder="Поиск по товарам..." 
              className="w-full p-2 pl-4 rounded text-black outline-none"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
            <Search className="absolute right-3 top-2 text-gray-400" size={20} />
          </div>

          <div className="flex items-center gap-6">
            <button onClick={() => setView('admin')} className="hover:bg-orange-600 px-3 py-2 rounded flex items-center gap-2">
              <Package size={20}/> Админка
            </button>
            {/* КНОПКА КОРЗИНЫ */}
            <div 
              className="relative cursor-pointer hover:bg-orange-600 p-2 rounded-full transition-colors"
              onClick={() => setIsCartOpen(true)}
            >
              <ShoppingCart size={28} />
              {cart.length > 0 && (
                <span className="absolute -top-1 -right-1 bg-white text-[#ff6700] text-xs font-bold px-1.5 py-0.5 rounded-full border-2 border-[#ff6700]">
                  {cart.reduce((sum, i) => sum + i.count, 0)}
                </span>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* МОДАЛКА КОРЗИНЫ */}
      {isCartOpen && (
        <div className="fixed inset-0 bg-black/50 z-[60] flex justify-end">
          <div className="w-full max-w-md bg-white h-full shadow-2xl p-6 overflow-y-auto">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-bold">Корзина</h2>
              <X className="cursor-pointer" onClick={() => setIsCartOpen(false)} />
            </div>
            {cart.length === 0 ? <p>Тут пока пусто...</p> : (
              <>
                {cart.map(item => (
                  <div key={item.name} className="flex justify-between items-center border-b py-4">
                    <div>
                      <div className="font-bold">{item.name}</div>
                      <div className="text-sm text-gray-500">{item.count} шт. x {item.price} ₽</div>
                    </div>
                    <button onClick={() => removeFromCart(item.name)} className="text-red-500"><Trash2 size={18}/></button>
                  </div>
                ))}
                <div className="mt-6">
                  <div className="text-xl font-bold mb-4">Итого: {cart.reduce((sum, i) => sum + (i.price * i.count), 0)} ₽</div>
                  <button onClick={handleCheckout} className="w-full bg-green-600 text-white py-3 rounded font-bold hover:bg-green-700">
                    Оформить заказ
                  </button>
                </div>
              </>
            )}
          </div>
        </div>
      )}

      <main className="container mx-auto p-6">
        {view === 'shop' ? (
          <>
            <h1 className="text-2xl font-bold mb-6 text-gray-800">
              {searchQuery ? `Результаты поиска: ${searchQuery}` : 'Каталог'}
            </h1>
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6">
              {filteredProducts.map((product, idx) => (
                <div key={idx} className="bg-white p-4 rounded-lg shadow-sm border flex flex-col justify-between h-full">
                  <div>
                    <div className="h-40 w-full mb-4 flex items-center justify-center bg-white">
                      <img src={`/${product.name}.png`} alt={product.name} className="max-h-full max-w-full object-contain" onError={(e) => {e.target.src = "https://placehold.co/200x150?text=Нет+фото"}} />
                    </div>
                    <h2 className="text-sm font-medium h-10 overflow-hidden">{product.name}</h2>
                  </div>
                  <div className="mt-4">
                    <div className="text-2xl font-extrabold mb-1">{product.price.toLocaleString()} ₽</div>
                    <div className={`text-[11px] mb-3 font-bold uppercase ${product.stock > 0 ? 'text-green-600' : 'text-red-500'}`}>
                      {product.stock > 0 ? `В наличии: ${product.stock}` : 'Нет на складе'}
                    </div>
                    <button 
                      onClick={() => addToCart(product)}
                      disabled={product.stock <= 0}
                      className={`w-full py-2 rounded font-bold transition-all ${product.stock > 0 ? 'bg-[#ff6700] text-white hover:bg-[#e65c00]' : 'bg-gray-200 text-gray-400'}`}
                    >
                      В корзину
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </>
        ) : (
          /* АДМИНКА (без изменений) */
          <div className="max-w-md mx-auto bg-white p-8 rounded-lg shadow-xl">
             <h2 className="text-2xl font-bold mb-6">Новый товар (Бэкенд)</h2>
             {/* ... формы остаются как были ... */}
             <form onSubmit={handleAddProduct} className="space-y-4">
                <input type="text" placeholder="Название" required className="w-full border p-2" value={newProduct.name} onChange={(e) => setNewProduct({...newProduct, name: e.target.value})}/>
                <input type="number" placeholder="Цена" required className="w-full border p-2" value={newProduct.price} onChange={(e) => setNewProduct({...newProduct, price: parseFloat(e.target.value)})}/>
                <input type="number" placeholder="Склад" required className="w-full border p-2" value={newProduct.stock} onChange={(e) => setNewProduct({...newProduct, stock: parseInt(e.target.value)})}/>
                <button type="submit" className="w-full bg-green-600 text-white py-2 rounded">Сохранить</button>
                <button type="button" onClick={() => setView('shop')} className="w-full mt-2">Отмена</button>
             </form>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;