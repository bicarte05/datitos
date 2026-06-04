-- Datos iniciales para la base de datos
-- Insertar países
INSERT INTO public.pais (nombre) VALUES ('Chile') ON CONFLICT DO NOTHING;
INSERT INTO public.pais (nombre) VALUES ('Argentina') ON CONFLICT DO NOTHING;
INSERT INTO public.pais (nombre) VALUES ('Perú') ON CONFLICT DO NOTHING;

-- Obtener ID de Chile
WITH chile_id AS (SELECT id_pais FROM public.pais WHERE nombre = 'Chile' LIMIT 1)
INSERT INTO public.ciudad (nombre, id_pais) 
SELECT 'Valdivia', id_pais FROM chile_id
WHERE NOT EXISTS (SELECT 1 FROM public.ciudad WHERE nombre = 'Valdivia')
ON CONFLICT DO NOTHING;

WITH chile_id AS (SELECT id_pais FROM public.pais WHERE nombre = 'Chile' LIMIT 1)
INSERT INTO public.ciudad (nombre, id_pais)
SELECT 'Puerto Varas', id_pais FROM chile_id
WHERE NOT EXISTS (SELECT 1 FROM public.ciudad WHERE nombre = 'Puerto Varas')
ON CONFLICT DO NOTHING;

WITH chile_id AS (SELECT id_pais FROM public.pais WHERE nombre = 'Chile' LIMIT 1)
INSERT INTO public.ciudad (nombre, id_pais)
SELECT 'Santiago', id_pais FROM chile_id
WHERE NOT EXISTS (SELECT 1 FROM public.ciudad WHERE nombre = 'Santiago')
ON CONFLICT DO NOTHING;

WITH chile_id AS (SELECT id_pais FROM public.pais WHERE nombre = 'Chile' LIMIT 1)
INSERT INTO public.ciudad (nombre, id_pais)
SELECT 'Concepción', id_pais FROM chile_id
WHERE NOT EXISTS (SELECT 1 FROM public.ciudad WHERE nombre = 'Concepción')
ON CONFLICT DO NOTHING;

-- Insertar tipos de suscripción
INSERT INTO public.suscripcion (tipo, costo_mensual, descuento_envio) VALUES ('Basic', 4990, 10) ON CONFLICT DO NOTHING;
INSERT INTO public.suscripcion (tipo, costo_mensual, descuento_envio) VALUES ('Premium', 9990, 25) ON CONFLICT DO NOTHING;
INSERT INTO public.suscripcion (tipo, costo_mensual, descuento_envio) VALUES ('VIP', 14990, 50) ON CONFLICT DO NOTHING;

-- Insertar comercios
WITH valdivia_id AS (SELECT id_ciudad FROM public.ciudad WHERE nombre = 'Valdivia' LIMIT 1)
INSERT INTO public.comercio (nombre, rubro, direccion, id_ciudad)
SELECT 'Pizza Los Datitos', 'Pizzería', 'Av. Ramón Picarte 1234', id_ciudad FROM valdivia_id
WHERE NOT EXISTS (SELECT 1 FROM public.comercio WHERE nombre = 'Pizza Los Datitos')
ON CONFLICT DO NOTHING;

WITH valdivia_id AS (SELECT id_ciudad FROM public.ciudad WHERE nombre = 'Valdivia' LIMIT 1)
INSERT INTO public.comercio (nombre, rubro, direccion, id_ciudad)
SELECT 'Burger King', 'Hamburguesas', 'General Lagos 567', id_ciudad FROM valdivia_id
WHERE NOT EXISTS (SELECT 1 FROM public.comercio WHERE nombre = 'Burger King')
ON CONFLICT DO NOTHING;

WITH valdivia_id AS (SELECT id_ciudad FROM public.ciudad WHERE nombre = 'Valdivia' LIMIT 1)
INSERT INTO public.comercio (nombre, rubro, direccion, id_ciudad)
SELECT 'Sushi Express', 'Sushi', 'Calle Picarte 890', id_ciudad FROM valdivia_id
WHERE NOT EXISTS (SELECT 1 FROM public.comercio WHERE nombre = 'Sushi Express')
ON CONFLICT DO NOTHING;

-- Insertar productos para Pizza Los Datitos
WITH comercio_id AS (SELECT id_comercio FROM public.comercio WHERE nombre = 'Pizza Los Datitos' LIMIT 1)
INSERT INTO public.producto (nombre, descripcion, precio, id_comercio)
SELECT 'Pizza Napolitana', 'Tomate, mozzarella y albahaca', 9990, id_comercio FROM comercio_id
WHERE NOT EXISTS (SELECT 1 FROM public.producto WHERE nombre = 'Pizza Napolitana' AND id_comercio = (SELECT id_comercio FROM public.comercio WHERE nombre = 'Pizza Los Datitos' LIMIT 1))
ON CONFLICT DO NOTHING;

WITH comercio_id AS (SELECT id_comercio FROM public.comercio WHERE nombre = 'Pizza Los Datitos' LIMIT 1)
INSERT INTO public.producto (nombre, descripcion, precio, id_comercio)
SELECT 'Pizza Pepperoni', 'Tomate, mozzarella y pepperoni', 11990, id_comercio FROM comercio_id
WHERE NOT EXISTS (SELECT 1 FROM public.producto WHERE nombre = 'Pizza Pepperoni' AND id_comercio = (SELECT id_comercio FROM public.comercio WHERE nombre = 'Pizza Los Datitos' LIMIT 1))
ON CONFLICT DO NOTHING;

WITH comercio_id AS (SELECT id_comercio FROM public.comercio WHERE nombre = 'Pizza Los Datitos' LIMIT 1)
INSERT INTO public.producto (nombre, descripcion, precio, id_comercio)
SELECT 'Pizza Supreme', 'Carnes surtidas, vegetales y queso', 14990, id_comercio FROM comercio_id
WHERE NOT EXISTS (SELECT 1 FROM public.producto WHERE nombre = 'Pizza Supreme' AND id_comercio = (SELECT id_comercio FROM public.comercio WHERE nombre = 'Pizza Los Datitos' LIMIT 1))
ON CONFLICT DO NOTHING;

-- Insertar productos para Burger King
WITH comercio_id AS (SELECT id_comercio FROM public.comercio WHERE nombre = 'Burger King' LIMIT 1)
INSERT INTO public.producto (nombre, descripcion, precio, id_comercio)
SELECT 'Whopper', 'Hamburguesa clásica con lechuga, tomate y salsa', 7990, id_comercio FROM comercio_id
WHERE NOT EXISTS (SELECT 1 FROM public.producto WHERE nombre = 'Whopper' AND id_comercio = (SELECT id_comercio FROM public.comercio WHERE nombre = 'Burger King' LIMIT 1))
ON CONFLICT DO NOTHING;

WITH comercio_id AS (SELECT id_comercio FROM public.comercio WHERE nombre = 'Burger King' LIMIT 1)
INSERT INTO public.producto (nombre, descripcion, precio, id_comercio)
SELECT 'Combo Burger King', 'Whopper + papas + bebida', 12990, id_comercio FROM comercio_id
WHERE NOT EXISTS (SELECT 1 FROM public.producto WHERE nombre = 'Combo Burger King' AND id_comercio = (SELECT id_comercio FROM public.comercio WHERE nombre = 'Burger King' LIMIT 1))
ON CONFLICT DO NOTHING;

WITH comercio_id AS (SELECT id_comercio FROM public.comercio WHERE nombre = 'Burger King' LIMIT 1)
INSERT INTO public.producto (nombre, descripcion, precio, id_comercio)
SELECT 'Papas Fritas', 'Papas crujientes', 3990, id_comercio FROM comercio_id
WHERE NOT EXISTS (SELECT 1 FROM public.producto WHERE nombre = 'Papas Fritas' AND id_comercio = (SELECT id_comercio FROM public.comercio WHERE nombre = 'Burger King' LIMIT 1))
ON CONFLICT DO NOTHING;

-- Insertar productos para Sushi Express
WITH comercio_id AS (SELECT id_comercio FROM public.comercio WHERE nombre = 'Sushi Express' LIMIT 1)
INSERT INTO public.producto (nombre, descripcion, precio, id_comercio)
SELECT 'Roll California', 'Cangrejo, aguacate y pepino', 8990, id_comercio FROM comercio_id
WHERE NOT EXISTS (SELECT 1 FROM public.producto WHERE nombre = 'Roll California' AND id_comercio = (SELECT id_comercio FROM public.comercio WHERE nombre = 'Sushi Express' LIMIT 1))
ON CONFLICT DO NOTHING;

WITH comercio_id AS (SELECT id_comercio FROM public.comercio WHERE nombre = 'Sushi Express' LIMIT 1)
INSERT INTO public.producto (nombre, descripcion, precio, id_comercio)
SELECT 'Roll Philadelphia', 'Salmón, queso crema y aguacate', 10990, id_comercio FROM comercio_id
WHERE NOT EXISTS (SELECT 1 FROM public.producto WHERE nombre = 'Roll Philadelphia' AND id_comercio = (SELECT id_comercio FROM public.comercio WHERE nombre = 'Sushi Express' LIMIT 1))
ON CONFLICT DO NOTHING;

WITH comercio_id AS (SELECT id_comercio FROM public.comercio WHERE nombre = 'Sushi Express' LIMIT 1)
INSERT INTO public.producto (nombre, descripcion, precio, id_comercio)
SELECT 'Nigiri Salmón', '2 piezas de salmón fresco', 6990, id_comercio FROM comercio_id
WHERE NOT EXISTS (SELECT 1 FROM public.producto WHERE nombre = 'Nigiri Salmón' AND id_comercio = (SELECT id_comercio FROM public.comercio WHERE nombre = 'Sushi Express' LIMIT 1))
ON CONFLICT DO NOTHING;

