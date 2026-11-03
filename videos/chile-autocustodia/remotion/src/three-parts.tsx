import React, {useMemo} from 'react';
import * as THREE from 'three';
import {useThree} from '@react-three/fiber';
import {cancelRender, continueRender, delayRender, staticFile} from 'remotion';

export const TERRA = '#A3482F';
export const TERRA_L = '#CD6C50';

// ---------- texturas carregadas antes do primeiro quadro ----------
const TEX: Record<string, THREE.Texture> = {};
const texHandle = delayRender('texturas');
Promise.all(
	['earth.jpg', 'chile.png', 'brasil.png', 'borders.png'].map(
		(name) =>
			new Promise<void>((res, rej) => {
				const img = new Image();
				img.crossOrigin = 'anonymous';
				img.onload = () => {
					const t = new THREE.Texture(img);
					t.colorSpace = THREE.SRGBColorSpace;
					t.anisotropy = 8;
					t.needsUpdate = true;
					TEX[name] = t;
					res();
				};
				img.onerror = (e) => rej(new Error('falha ao carregar ' + name));
				img.src = staticFile(name);
			}),
	),
)
	.then(() => continueRender(texHandle))
	.catch((e) => cancelRender(e));
export const useTex = (name: string) => TEX[name] ?? null;

// ---------- utilidades ----------
export const clamp01 = (x: number) => Math.max(0, Math.min(1, x));
export const ease = (x: number) => 1 - Math.pow(1 - clamp01(x), 3);
export const eio = (x: number) => {
	const t = clamp01(x);
	return t * t * (3 - 2 * t);
};
const rand = (seed: number) => {
	let s = seed;
	return () => {
		s = (s * 16807) % 2147483647;
		return (s - 1) / 2147483646;
	};
};

// ---------- câmera ----------
export const CamRig: React.FC<{pos: [number, number, number]; look?: [number, number, number]; fov?: number}> = ({pos, look = [0, 0, 0], fov = 35}) => {
	const {camera} = useThree();
	camera.position.set(...pos);
	(camera as THREE.PerspectiveCamera).fov = fov;
	(camera as THREE.PerspectiveCamera).updateProjectionMatrix();
	camera.lookAt(...look);
	return null;
};

// ---------- estrelas ----------
export const Stars: React.FC<{opacity?: number}> = ({opacity = 0.8}) => {
	const geo = useMemo(() => {
		const r = rand(42);
		const n = 1400;
		const arr = new Float32Array(n * 3);
		for (let i = 0; i < n; i++) {
			const u = r() * 2 - 1, th = r() * Math.PI * 2, rad = 30 + r() * 20;
			const s = Math.sqrt(1 - u * u);
			arr[i * 3] = rad * s * Math.cos(th);
			arr[i * 3 + 1] = rad * u;
			arr[i * 3 + 2] = rad * s * Math.sin(th);
		}
		const g = new THREE.BufferGeometry();
		g.setAttribute('position', new THREE.BufferAttribute(arr, 3));
		return g;
	}, []);
	return (
		<points geometry={geo}>
			<pointsMaterial size={0.09} color="#ffffff" transparent opacity={opacity} sizeAttenuation />
		</points>
	);
};

// ---------- globo ----------
const lonLatToVec = (lon: number, lat: number, r: number) => {
	const phi = ((lon + 180) / 360) * Math.PI * 2;
	const th = ((90 - lat) / 180) * Math.PI;
	return new THREE.Vector3(-r * Math.cos(phi) * Math.sin(th), r * Math.cos(th), r * Math.sin(phi) * Math.sin(th));
};

type Rede = {nodes: [number, number, number][]; edges: [number, number][]};

export const Globe: React.FC<{lon: number; lat: number; chile: number; brasil: number; rede: Rede | null; redeP: number; time: number}> = ({lon, lat, chile, brasil, rede, redeP, time}) => {
	const earth = useTex('earth.jpg');
	const tChile = useTex('chile.png');
	const tBr = useTex('brasil.png');
	const tBorders = useTex('borders.png');
	const phi = ((lon + 180) / 360) * Math.PI * 2;
	const ry = Math.PI / 2 - phi;
	const rx = (lat * Math.PI) / 180;

	const lines = useMemo(() => {
		if (!rede || redeP <= 0) return [] as THREE.Line[];
		const mat = new THREE.LineBasicMaterial({color: '#D4AF6A', transparent: true, opacity: 0.9});
		return rede.edges
			.map(([i, j]) => {
				const a = rede.nodes[i], b = rede.nodes[j];
				const q = clamp01(redeP * 1.7 - a[2] * 0.7);
				if (q <= 0) return null;
				const va = lonLatToVec(a[0], a[1], 1), vb = lonLatToVec(b[0], b[1], 1);
				const pts: THREE.Vector3[] = [];
				const steps = 24;
				for (let k = 0; k <= Math.round(steps * q); k++) {
					const s = k / steps;
					const v = va.clone().lerp(vb, s).normalize().multiplyScalar(1.006 + Math.sin(Math.PI * s) * 0.05);
					pts.push(v);
				}
				if (pts.length < 2) return null;
				return new THREE.Line(new THREE.BufferGeometry().setFromPoints(pts), mat);
			})
			.filter(Boolean) as THREE.Line[];
	}, [rede, redeP]);

	if (!earth || !tChile || !tBr || !tBorders)
		return (
			<mesh>
				<sphereGeometry args={[1, 64, 64]} />
				<meshStandardMaterial color="#ff00ff" />
			</mesh>
		);
	return (
		<group rotation-x={rx}>
			<group rotation-y={ry}>
				<mesh>
					<sphereGeometry args={[1, 160, 160]} />
					<meshStandardMaterial map={earth} roughness={0.95} metalness={0} />
				</mesh>
				<mesh>
					<sphereGeometry args={[1.0015, 160, 160]} />
					<meshBasicMaterial map={tBorders} transparent opacity={0.9} depthWrite={false} />
				</mesh>
				<mesh>
					<sphereGeometry args={[1.003, 160, 160]} />
					<meshBasicMaterial map={tBr} transparent opacity={brasil} depthWrite={false} />
				</mesh>
				<mesh>
					<sphereGeometry args={[1.004, 160, 160]} />
					<meshBasicMaterial map={tChile} transparent opacity={chile} depthWrite={false} />
				</mesh>
				{lines.map((l, k) => (
					<primitive key={k} object={l} />
				))}
				{rede && redeP > 0
					? rede.nodes.map((n, k) => {
							const q = clamp01(redeP * 1.7 - n[2] * 0.7);
							if (q <= 0) return null;
							const v = lonLatToVec(n[0], n[1], 1.008);
							const s = 0.008 + 0.004 * Math.sin(time * 4 + n[2] * 10);
							return (
								<mesh key={'n' + k} position={v} scale={s * q}>
									<sphereGeometry args={[1, 10, 10]} />
									<meshBasicMaterial color="#f3dca6" />
								</mesh>
							);
						})
					: null}
			</group>
			{/* atmosfera */}
			<mesh>
				<sphereGeometry args={[1.06, 64, 64]} />
				<meshBasicMaterial color="#7fa6d6" transparent opacity={0.08} side={THREE.BackSide} />
			</mesh>
		</group>
	);
};

// ---------- prédio 3D andar por andar ----------
export const Building: React.FC<{floors: number; p: number; time: number; warm?: boolean}> = ({floors, p, time, warm}) => {
	const shown = p * floors;
	return (
		<group rotation-y={-0.6 + time * 0.25}>
			{Array.from({length: floors}).map((_, i) => {
				const q = clamp01(shown - i);
				if (q <= 0) return null;
				const y = i * 0.2 + (1 - ease(q)) * 0.6;
				return (
					<group key={i} position={[0, y, 0]} scale={[1, ease(q), 1]}>
						<mesh>
							<boxGeometry args={[1, 0.18, 1]} />
							<meshStandardMaterial color="#1c1d22" metalness={0.5} roughness={0.35} />
						</mesh>
						{[-1, 1].map((side) => (
							<mesh key={side} position={[0, 0, 0.502 * side]}>
								<planeGeometry args={[0.86, 0.09]} />
								<meshStandardMaterial
									color={warm ? '#ffcf9e' : '#dbe9ff'}
									emissive={warm ? '#ff9a5a' : '#9cc4ff'}
									emissiveIntensity={0.6 + 0.4 * Math.sin(i * 1.7 + time * 2)}
									side={THREE.DoubleSide}
								/>
							</mesh>
						))}
						{[-1, 1].map((side) => (
							<mesh key={'s' + side} position={[0.502 * side, 0, 0]} rotation-y={Math.PI / 2}>
								<planeGeometry args={[0.86, 0.09]} />
								<meshStandardMaterial color="#dbe9ff" emissive="#6f9bd8" emissiveIntensity={0.5} side={THREE.DoubleSide} />
							</mesh>
						))}
					</group>
				);
			})}
			<mesh rotation-x={-Math.PI / 2} position={[0, -0.12, 0]}>
				<circleGeometry args={[1.6, 64]} />
				<meshBasicMaterial color="#3E6EA8" transparent opacity={0.16} />
			</mesh>
		</group>
	);
};

// ---------- bloco de contrato que congela ----------
export const IceBlock: React.FC<{freeze: number; time: number}> = ({freeze, time}) => {
	const c = new THREE.Color('#E9E4D8').lerp(new THREE.Color('#d6ecff'), freeze);
	return (
		<group rotation={[0.35, -0.5 + time * 0.3, 0.08]}>
			<mesh>
				<boxGeometry args={[1.1, 1.5, 0.14]} />
				<meshStandardMaterial color={c} metalness={0.2 + 0.5 * freeze} roughness={0.4 - 0.25 * freeze} emissive={c} emissiveIntensity={0.15 + 0.25 * freeze} />
			</mesh>
			{[0.45, 0.25, 0.05, -0.15, -0.35].map((y, k) => (
				<mesh key={k} position={[0, y, 0.075]}>
					<planeGeometry args={[0.8 - (k % 2) * 0.2, 0.05]} />
					<meshBasicMaterial color="#f2eee8" transparent opacity={0.85} />
				</mesh>
			))}
			<mesh scale={1 + 0.12 * freeze}>
				<boxGeometry args={[1.25, 1.65, 0.3]} />
				<meshStandardMaterial color="#e8f6ff" transparent opacity={0.28 * freeze} roughness={0.05} metalness={0.1} />
			</mesh>
		</group>
	);
};

// ---------- porta de cofre ----------
export const Vault: React.FC<{close: number; spin: number}> = ({close, spin}) => {
	const metal = {color: '#3b3e46', metalness: 0.9, roughness: 0.32} as const;
	return (
		<group>
			<mesh rotation-x={Math.PI / 2}>
				<torusGeometry args={[1.08, 0.08, 24, 96]} />
				<meshStandardMaterial {...metal} color="#2a2c32" />
			</mesh>
			<group position={[-1, 0, 0]} rotation-y={-1.35 * (1 - ease(close))}>
				<group position={[1, 0, 0]}>
					<mesh rotation-x={Math.PI / 2}>
						<cylinderGeometry args={[1, 1, 0.22, 96]} />
						<meshStandardMaterial {...metal} />
					</mesh>
					<mesh position={[0, 0, 0.115]}>
						<ringGeometry args={[0.55, 0.62, 96]} />
						<meshStandardMaterial color="#D4AF6A" metalness={0.9} roughness={0.25} emissive="#6b5420" emissiveIntensity={0.3} />
					</mesh>
					{Array.from({length: 10}).map((_, k) => {
						const a = (k / 10) * Math.PI * 2;
						return (
							<mesh key={k} position={[Math.cos(a) * 0.85, Math.sin(a) * 0.85, 0.12]} rotation-x={Math.PI / 2}>
								<cylinderGeometry args={[0.05, 0.05, 0.06, 20]} />
								<meshStandardMaterial color="#9a9ca3" metalness={1} roughness={0.25} />
							</mesh>
						);
					})}
					<group position={[0, 0, 0.17]} rotation-z={spin * Math.PI * 1.5}>
						<mesh>
							<torusGeometry args={[0.32, 0.035, 16, 64]} />
							<meshStandardMaterial color="#c9ccd3" metalness={1} roughness={0.2} />
						</mesh>
						{[0, 1, 2].map((k) => (
							<mesh key={k} rotation-z={(k * Math.PI * 2) / 3}>
								<boxGeometry args={[0.64, 0.04, 0.04]} />
								<meshStandardMaterial color="#c9ccd3" metalness={1} roughness={0.2} />
							</mesh>
						))}
					</group>
				</group>
			</group>
		</group>
	);
};

// ---------- chave 3D ----------
export const Key3D: React.FC<{p: number; time: number}> = ({p, time}) => {
	const mat = {color: '#D4AF37', metalness: 0.95, roughness: 0.22, emissive: '#5a4512', emissiveIntensity: 0.35} as const;
	return (
		<group scale={0.2 + 0.8 * ease(p)} rotation={[0.25, time * 1.1, -0.35]}>
			<mesh position={[-0.75, 0, 0]}>
				<torusGeometry args={[0.36, 0.1, 32, 96]} />
				<meshStandardMaterial {...mat} />
			</mesh>
			<mesh position={[0.25, 0, 0]} rotation-z={Math.PI / 2}>
				<cylinderGeometry args={[0.075, 0.075, 1.3, 32]} />
				<meshStandardMaterial {...mat} />
			</mesh>
			{[0.55, 0.75].map((x, k) => (
				<mesh key={k} position={[x, -0.15 - k * 0.04, 0]}>
					<boxGeometry args={[0.1, 0.22 + k * 0.08, 0.1]} />
					<meshStandardMaterial {...mat} />
				</mesh>
			))}
		</group>
	);
};
