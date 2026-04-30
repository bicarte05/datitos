
SELECT 'pedido' AS tabla_transaccional, COUNT(*) AS total_registros FROM public.pedido
UNION ALL
SELECT 'detalle_pedido', COUNT(*) FROM public.detalle_pedido
UNION ALL
SELECT 'pago', COUNT(*) FROM public.pago
UNION ALL
SELECT 'valoracion_pedido', COUNT(*) FROM public.valoracion_pedido
UNION ALL
SELECT 'reclamo', COUNT(*) FROM public.reclamo
UNION ALL
SELECT 'carrito', COUNT(*) FROM public.carrito
UNION ALL
SELECT 'item_carrito', COUNT(*) FROM public.item_carrito
UNION ALL
SELECT 'item_carrito_complemento', COUNT(*) FROM public.item_carrito_complemento
ORDER BY total_registros DESC;
