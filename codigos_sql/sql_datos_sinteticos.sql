

-- Pais y ciudades
INSERT INTO public.pais (id_pais, nombre) VALUES (1, 'Chile');
INSERT INTO public.ciudad (id_ciudad, nombre, id_pais) VALUES 
(1, 'Valdivia', 1), (2, 'Santiago', 1), (3, 'Concepción', 1), (4, 'Temuco', 1), (5, 'Puerto Montt', 1), (6, 'Punta Arenas', 1);

-- Planes de suscripcion
INSERT INTO public.suscripcion (id_suscripcion, tipo, costo_mensual, descuento_envio) VALUES
(1, 'Gratis', 0, 0), (2, 'Plus', 4990, 50), (3, 'Premium', 9990, 100);

-- Cupones
INSERT INTO public.cupon (codigo, porcentaje, fecha_expira, estado) VALUES 
('BIENVENIDA', 20.00, '2026-12-31', 'Activo'),
('PROMO_UACH', 15.00, '2026-06-30', 'Activo'),
('DATITOS', 10.00, '2026-05-30', 'Activo'),
('PYTHONES', 100.00, '2026-12-31', 'Activo'), 
('DESC_SORPRESA', 5.00, '2026-04-30', 'Activo');

-- Clientes Repartidores Comercios
INSERT INTO public.cliente (nombre, email, telefono, id_suscripcion)
SELECT 
    (ARRAY['Camilo', 'Luca', 'Camila', 'Ian', 'Valentina', 'Matías', 'Fernanda', 'Basti', 'Ignacia', 'Benjamín'])[floor(random() * 10 + 1)] || ' ' ||
    (ARRAY['Muñoz', 'Rojas', 'Díaz', 'Soto', 'Silva', 'Sepúlveda', 'Castro', 'Tapia', 'Araya', 'Pizarro'])[floor(random() * 10 + 1)],
    'user' || i || '@gmail.com', '+569' || (10000000 + i), (floor(random() * 3) + 1)
FROM generate_series(1, 500) AS i;

INSERT INTO public.repartidor (nombre, vehiculo, telefono, calificacion_promedio, id_ciudad)
SELECT 
    (ARRAY['Andrés', 'Felipe', 'Cristian', 'Rodrigo', 'Marcelo', 'Juan', 'Luis'])[floor(random() * 7 + 1)] || ' ' ||
    (ARRAY['González', 'López', 'Rodríguez', 'García', 'Pérez', 'Vargas'])[floor(random() * 6 + 1)],
    (ARRAY['Moto', 'Bicicleta', 'Auto'])[floor(random() * 3 + 1)],
    '+569' || (20000000 + i), round((random() * 2 + 3)::numeric, 2), (floor(random() * 5) + 1)
FROM generate_series(1, 100) AS i;

INSERT INTO public.comercio (nombre, rubro, direccion, id_ciudad)
SELECT 
    (ARRAY['Picada', 'Restaurante', 'Farmacia', 'Market', 'Botillería', 'Tienda'])[floor(random() * 6 + 1)] || ' ' ||
    (ARRAY['La Teja', 'Calle-Calle', 'Picarte', 'Sur', 'Ríos', 'Central', 'Plaza'])[floor(random() * 7 + 1)],
    (ARRAY['Restaurante', 'Farmacia', 'Supermercado', 'Botillería', 'Mascotas', 'Tecnología'])[floor(random() * 6 + 1)],
    'Calle ' || i, (floor(random() * 5) + 1)
FROM generate_series(1, 50) AS i;

-- Direcciones
INSERT INTO public.direccion (id_cliente, calle, numero, id_ciudad)
SELECT id_cliente, (ARRAY['Av. Alemania', 'Picarte', 'Los Robles', 'Esmeralda'])[floor(random()*4+1)], floor(random()*5000+1)::text, (floor(random()*5)+1)
FROM public.cliente;

-- Productos
INSERT INTO public.producto (nombre, precio, id_comercio)
SELECT 
    CASE c.rubro
        WHEN 'Restaurante' THEN 'Hamburguesa Doble Queso'
        WHEN 'Farmacia' THEN 'Paracetamol 500mg'
        WHEN 'Supermercado' THEN 'Arroz 1kg'
        WHEN 'Botillería' THEN 'Pisco 35°'
        WHEN 'Mascotas' THEN 'Alimento Perro 3kg'
        WHEN 'Tecnología' THEN 'Audífonos Bluetooth'
        ELSE 'Pack Oferta'
    END, (random() * 5000 + 3000), id_comercio
FROM public.comercio c;

INSERT INTO public.producto (nombre, precio, id_comercio)
SELECT 
    CASE c.rubro
        WHEN 'Restaurante' THEN 'Pizza Pepperoni'
        WHEN 'Farmacia' THEN 'Alcohol Gel'
        WHEN 'Supermercado' THEN 'Leche Entera'
        WHEN 'Botillería' THEN 'Pack Cerveza 6un'
        WHEN 'Mascotas' THEN 'Arena Gatos'
        WHEN 'Tecnología' THEN 'Cable USB-C'
        ELSE 'Promo'
    END, (random() * 4000 + 1500), id_comercio
FROM public.comercio c;

-- Complementos
INSERT INTO public.complemento (nombre, precio_extra) VALUES 
('Mayo Casera', 500), ('Doble Queso', 1200), ('Tocino Crujiente', 1500),
('Bolsa Térmica (Frío)', 2000), ('Bolsa Biodegradable', 200),
('Seguro contra Robo', 15000), ('Garantía Extendida', 8000),
('Despacho Express', 2500);

-- Pedidos (transaccional)
INSERT INTO public.pedido (id_pedido, fecha, total_productos, costo_envio, distancia_km, id_cliente, id_comercio, id_repartidor, id_cupon)
SELECT 
    i, 
    NOW() - (random() * interval '4 years'), 
    0.00, 
    round((random() * 3000 + 1000)::numeric, 2),
    round((random() * 8 + 1)::numeric, 2),
    (SELECT id_cliente FROM public.cliente OFFSET floor(random() * 500) LIMIT 1),
    (SELECT id_comercio FROM public.comercio OFFSET floor(random() * 50) LIMIT 1),
    (SELECT id_repartidor FROM public.repartidor OFFSET floor(random() * 100) LIMIT 1),
    -- El 15% de los pedidos tendrá un cupón aleatorio, el resto null
    CASE 
        WHEN random() < 0.15 THEN (SELECT id_cupon FROM public.cupon ORDER BY random() LIMIT 1)
        ELSE NULL 
    END
FROM generate_series(1, 10000) AS i;

-- Detalle Pedido
INSERT INTO public.detalle_pedido (id_pedido, id_producto, cantidad, precio_unitario)
SELECT 
    p.id_pedido,
    prod.id_producto,
    (p.id_pedido % 2) + 1, 
    prod.precio
FROM public.pedido p
JOIN LATERAL (
    SELECT id_producto, precio 
    FROM public.producto 
    WHERE id_comercio = p.id_comercio 
    ORDER BY id_producto
    OFFSET (p.id_pedido % 2) LIMIT 1
) prod ON true;

-- Actualizar los totales del pedido según sus productos
UPDATE public.pedido p SET total_productos = COALESCE((SELECT SUM(cantidad * precio_unitario) FROM public.detalle_pedido WHERE id_pedido = p.id_pedido), 0);

-- Pagos Valoracion Reclamos
INSERT INTO public.pago (id_pedido, metodo_pago, monto_final, estado, fecha_pago)
SELECT 
    p.id_pedido, 
    (ARRAY['Débito', 'Crédito', 'Efectivo'])[floor(random()*3+1)], 
    -- Lógica: (Total Productos * (1 - Descuento/100)) + Costo Envío
    round(
        (p.total_productos * (1 - COALESCE(c.porcentaje, 0) / 100)) + p.costo_envio, 
    2),
    'Aprobado', 
    p.fecha 
FROM public.pedido p
LEFT JOIN public.cupon c ON p.id_cupon = c.id_cupon;

INSERT INTO public.valoracion_pedido (id_pedido, nota_comercio, nota_repartidor, comentario)
SELECT id_pedido, floor(random()*2+4), floor(random()*2+4),
(ARRAY['Rico', 'Rápido', 'Excelente', 'Podría mejorar', 'Genial', 'Masomenos'])[floor(random()*5+1)]
FROM public.pedido WHERE random() < 0.3;

INSERT INTO public.reclamo (id_pedido, descripcion, estado)
SELECT id_pedido, 'Demora en la entrega', 'Cerrado' FROM public.pedido WHERE random() < 0.02;

-- Carritos Complementos
INSERT INTO public.carrito (id_cliente, fecha_creacion)
SELECT id_cliente, NOW() FROM public.cliente ORDER BY random() LIMIT 100;

INSERT INTO public.item_carrito (id_carrito, id_producto, cantidad)
SELECT c.id_carrito, (SELECT id_producto FROM public.producto ORDER BY random() LIMIT 1), 1
FROM public.carrito c;

INSERT INTO public.item_carrito_complemento (id_item_carrito, id_complemento)
SELECT ic.id_item, comp.id_complemento
FROM public.item_carrito ic
JOIN public.producto p ON ic.id_producto = p.id_producto
JOIN public.comercio c ON p.id_comercio = c.id_comercio
CROSS JOIN LATERAL (
    SELECT id_complemento FROM public.complemento
    WHERE 
        (c.rubro = 'Restaurante' AND nombre IN ('Mayo Casera', 'Doble Queso', 'Tocino Crujiente')) OR
        (c.rubro = 'Farmacia' AND nombre IN ('Bolsa Biodegradable', 'Bolsa Térmica (Frío)')) OR
        (c.rubro = 'Tecnología' AND nombre IN ('Seguro contra Robo', 'Garantía Extendida')) OR
        (nombre = 'Despacho Express')
    ORDER BY random() LIMIT 1
) comp;

