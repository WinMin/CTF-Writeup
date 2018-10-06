#include <assert.h>
#include <math.h>
#include <stdlib.h>
#include <string.h>

#include "../test.h"
#define UNLIKELY(x) __builtin_expect(!!(x), 0)
#define LIKELY(x) __builtin_expect(!!(x), 1)

#define TRAP(x) (wasm_rt_trap(WASM_RT_TRAP_##x), 0)

#define FUNC_PROLOGUE                                            \
  if (++wasm_rt_call_stack_depth > WASM_RT_MAX_CALL_STACK_DEPTH) \
    TRAP(EXHAUSTION)

#define FUNC_EPILOGUE --wasm_rt_call_stack_depth

#define UNREACHABLE TRAP(UNREACHABLE)

#define CALL_INDIRECT(table, t, ft, x, ...)          \
  (LIKELY((x) < table.size && table.data[x].func &&  \
          table.data[x].func_type == func_types[ft]) \
       ? ((t)table.data[x].func)(__VA_ARGS__)        \
       : TRAP(CALL_INDIRECT))

#define MEMCHECK(mem, a, t)  \
  if (UNLIKELY((a) + sizeof(t) > mem->size)) TRAP(OOB)

#define DEFINE_LOAD(name, t1, t2, t3)              \
  static inline t3 name(wasm_rt_memory_t* mem, u64 addr) {   \
    MEMCHECK(mem, addr, t1);                       \
    t1 result;                                     \
    memcpy(&result, &mem->data[addr], sizeof(t1)); \
    return (t3)(t2)result;                         \
  }

#define DEFINE_STORE(name, t1, t2)                           \
  static inline void name(wasm_rt_memory_t* mem, u64 addr, t2 value) { \
    MEMCHECK(mem, addr, t1);                                 \
    t1 wrapped = (t1)value;                                  \
    memcpy(&mem->data[addr], &wrapped, sizeof(t1));          \
  }

DEFINE_LOAD(i32_load, u32, u32, u32);
DEFINE_LOAD(i64_load, u64, u64, u64);
DEFINE_LOAD(f32_load, f32, f32, f32);
DEFINE_LOAD(f64_load, f64, f64, f64);
DEFINE_LOAD(i32_load8_s, s8, s32, u32);
DEFINE_LOAD(i64_load8_s, s8, s64, u64);
DEFINE_LOAD(i32_load8_u, u8, u32, u32);
DEFINE_LOAD(i64_load8_u, u8, u64, u64);
DEFINE_LOAD(i32_load16_s, s16, s32, u32);
DEFINE_LOAD(i64_load16_s, s16, s64, u64);
DEFINE_LOAD(i32_load16_u, u16, u32, u32);
DEFINE_LOAD(i64_load16_u, u16, u64, u64);
DEFINE_LOAD(i64_load32_s, s32, s64, u64);
DEFINE_LOAD(i64_load32_u, u32, u64, u64);
DEFINE_STORE(i32_store, u32, u32);
DEFINE_STORE(i64_store, u64, u64);
DEFINE_STORE(f32_store, f32, f32);
DEFINE_STORE(f64_store, f64, f64);
DEFINE_STORE(i32_store8, u8, u32);
DEFINE_STORE(i32_store16, u16, u32);
DEFINE_STORE(i64_store8, u8, u64);
DEFINE_STORE(i64_store16, u16, u64);
DEFINE_STORE(i64_store32, u32, u64);

#define I32_CLZ(x) ((x) ? __builtin_clz(x) : 32)
#define I64_CLZ(x) ((x) ? __builtin_clzll(x) : 64)
#define I32_CTZ(x) ((x) ? __builtin_ctz(x) : 32)
#define I64_CTZ(x) ((x) ? __builtin_ctzll(x) : 64)
#define I32_POPCNT(x) (__builtin_popcount(x))
#define I64_POPCNT(x) (__builtin_popcountll(x))

#define DIV_S(ut, min, x, y)                                 \
   ((UNLIKELY((y) == 0)) ?                TRAP(DIV_BY_ZERO)  \
  : (UNLIKELY((x) == min && (y) == -1)) ? TRAP(INT_OVERFLOW) \
  : (ut)((x) / (y)))

#define REM_S(ut, min, x, y)                                \
   ((UNLIKELY((y) == 0)) ?                TRAP(DIV_BY_ZERO) \
  : (UNLIKELY((x) == min && (y) == -1)) ? 0                 \
  : (ut)((x) % (y)))

#define I32_DIV_S(x, y) DIV_S(u32, INT32_MIN, (s32)x, (s32)y)
#define I64_DIV_S(x, y) DIV_S(u64, INT64_MIN, (s64)x, (s64)y)
#define I32_REM_S(x, y) REM_S(u32, INT32_MIN, (s32)x, (s32)y)
#define I64_REM_S(x, y) REM_S(u64, INT64_MIN, (s64)x, (s64)y)

#define DIVREM_U(op, x, y) \
  ((UNLIKELY((y) == 0)) ? TRAP(DIV_BY_ZERO) : ((x) op (y)))

#define DIV_U(x, y) DIVREM_U(/, x, y)
#define REM_U(x, y) DIVREM_U(%, x, y)

#define ROTL(x, y, mask) \
  (((x) << ((y) & (mask))) | ((x) >> (((mask) - (y) + 1) & (mask))))
#define ROTR(x, y, mask) \
  (((x) >> ((y) & (mask))) | ((x) << (((mask) - (y) + 1) & (mask))))

#define I32_ROTL(x, y) ROTL(x, y, 31)
#define I64_ROTL(x, y) ROTL(x, y, 63)
#define I32_ROTR(x, y) ROTR(x, y, 31)
#define I64_ROTR(x, y) ROTR(x, y, 63)

#define FMIN(x, y)                                          \
   ((UNLIKELY((x) != (x))) ? NAN                            \
  : (UNLIKELY((y) != (y))) ? NAN                            \
  : (UNLIKELY((x) == 0 && (y) == 0)) ? (signbit(x) ? x : y) \
  : (x < y) ? x : y)

#define FMAX(x, y)                                          \
   ((UNLIKELY((x) != (x))) ? NAN                            \
  : (UNLIKELY((y) != (y))) ? NAN                            \
  : (UNLIKELY((x) == 0 && (y) == 0)) ? (signbit(x) ? y : x) \
  : (x > y) ? x : y)

#define TRUNC_S(ut, st, ft, min, max, maxop, x)                             \
   ((UNLIKELY((x) != (x))) ? TRAP(INVALID_CONVERSION)                       \
  : (UNLIKELY((x) < (ft)(min) || (x) maxop (ft)(max))) ? TRAP(INT_OVERFLOW) \
  : (ut)(st)(x))

#define I32_TRUNC_S_F32(x) TRUNC_S(u32, s32, f32, INT32_MIN, INT32_MAX, >=, x)
#define I64_TRUNC_S_F32(x) TRUNC_S(u64, s64, f32, INT64_MIN, INT64_MAX, >=, x)
#define I32_TRUNC_S_F64(x) TRUNC_S(u32, s32, f64, INT32_MIN, INT32_MAX, >,  x)
#define I64_TRUNC_S_F64(x) TRUNC_S(u64, s64, f64, INT64_MIN, INT64_MAX, >=, x)

#define TRUNC_U(ut, ft, max, maxop, x)                                    \
   ((UNLIKELY((x) != (x))) ? TRAP(INVALID_CONVERSION)                     \
  : (UNLIKELY((x) <= (ft)-1 || (x) maxop (ft)(max))) ? TRAP(INT_OVERFLOW) \
  : (ut)(x))

#define I32_TRUNC_U_F32(x) TRUNC_U(u32, f32, UINT32_MAX, >=, x)
#define I64_TRUNC_U_F32(x) TRUNC_U(u64, f32, UINT64_MAX, >=, x)
#define I32_TRUNC_U_F64(x) TRUNC_U(u32, f64, UINT32_MAX, >,  x)
#define I64_TRUNC_U_F64(x) TRUNC_U(u64, f64, UINT64_MAX, >=, x)

#define DEFINE_REINTERPRET(name, t1, t2)  \
  static inline t2 name(t1 x) {           \
    t2 result;                            \
    memcpy(&result, &x, sizeof(result));  \
    return result;                        \
  }

DEFINE_REINTERPRET(f32_reinterpret_i32, u32, f32)
DEFINE_REINTERPRET(i32_reinterpret_f32, f32, u32)
DEFINE_REINTERPRET(f64_reinterpret_i64, u64, f64)
DEFINE_REINTERPRET(i64_reinterpret_f64, f64, u64)


static u32 func_types[5];

static void init_func_types(void) {
  func_types[0] = wasm_rt_register_func_type(4, 1, WASM_RT_I32, WASM_RT_I32, WASM_RT_I32, WASM_RT_I32, WASM_RT_I32);
  func_types[1] = wasm_rt_register_func_type(1, 0, WASM_RT_I32);
  func_types[2] = wasm_rt_register_func_type(0, 0);
  func_types[3] = wasm_rt_register_func_type(5, 1, WASM_RT_I32, WASM_RT_I32, WASM_RT_I32, WASM_RT_I32, WASM_RT_I32, WASM_RT_I32);
  func_types[4] = wasm_rt_register_func_type(3, 1, WASM_RT_I32, WASM_RT_I32, WASM_RT_I32, WASM_RT_I32);
}

static void f1(void);
static u32 f2(u32, u32, u32, u32);
static u32 f3(u32, u32, u32, u32);
static u32 f4(u32, u32, u32, u32);
static u32 f5(u32, u32, u32, u32);
static u32 f6(u32, u32, u32, u32);
static u32 f7(u32, u32, u32, u32);
static u32 f8(u32, u32, u32, u32);
static u32 f9(u32, u32, u32, u32, u32);
static u32 Match(u32, u32, u32, u32);
static u32 writev_c(u32, u32, u32);

static u32 g0;
static u32 __heap_base;
static u32 __data_end;

static void init_globals(void) {
  g0 = 66592u;
  __heap_base = 66592u;
  __data_end = 1052u;
}

static wasm_rt_memory_t memory;

static wasm_rt_table_t T0;

static void f1(void) {
  FUNC_PROLOGUE;
  FUNC_EPILOGUE;
}

static u32 f2(u32 p0, u32 p1, u32 p2, u32 p3) {
  u32 l0 = 0, l1 = 0, l2 = 0, l3 = 0, l4 = 0, l5 = 0, l6 = 0, l7 = 0, 
      l8 = 0, l9 = 0, l10 = 0, l11 = 0, l12 = 0, l13 = 0, l14 = 0, l15 = 0, 
      l16 = 0, l17 = 0, l18 = 0, l19 = 0, l20 = 0, l21 = 0, l22 = 0, l23 = 0, 
      l24 = 0, l25 = 0, l26 = 0, l27 = 0, l28 = 0, l29 = 0, l30 = 0, l31 = 0;
  FUNC_PROLOGUE;
  u32 i0, i1;
  i0 = g0;
  l0 = i0;
  i0 = 32u;
  l1 = i0;
  i0 = l0;
  i1 = l1;
  i0 -= i1;
  l2 = i0;
  i0 = 2u;
  l3 = i0;
  i0 = l2;
  i1 = p0;
  i32_store((&memory), (u64)(i0 + 20), i1);
  i0 = l2;
  i1 = p1;
  i32_store((&memory), (u64)(i0 + 16), i1);
  i0 = l2;
  i1 = p2;
  i32_store((&memory), (u64)(i0 + 12), i1);
  i0 = l2;
  i1 = p3;
  i32_store((&memory), (u64)(i0 + 8), i1);
  i0 = l2;
  i0 = i32_load((&memory), (u64)(i0 + 16));
  l4 = i0;
  i0 = l3;
  l5 = i0;
  i0 = l4;
  l6 = i0;
  i0 = l5;
  i1 = l6;
  i0 = i0 > i1;
  l7 = i0;
  i0 = l7;
  l8 = i0;
  i0 = l8;
  i0 = !(i0);
  if (i0) {goto B1;}
  i0 = 105u;
  l9 = i0;
  i0 = l2;
  i1 = l9;
  i32_store((&memory), (u64)(i0 + 24), i1);
  goto B0;
  B1:;
  i0 = 0u;
  l10 = i0;
  i0 = l2;
  i0 = i32_load((&memory), (u64)(i0 + 20));
  l11 = i0;
  i0 = l11;
  i0 = i32_load8_u((&memory), (u64)(i0));
  l12 = i0;
  i0 = l2;
  i1 = l12;
  i32_store8((&memory), (u64)(i0 + 31), i1);
  i0 = l2;
  i0 = i32_load8_u((&memory), (u64)(i0 + 31));
  l13 = i0;
  i0 = 255u;
  l14 = i0;
  i0 = l13;
  i1 = l14;
  i0 &= i1;
  l15 = i0;
  i0 = 15u;
  l16 = i0;
  i0 = l15;
  i1 = l16;
  i0 &= i1;
  l17 = i0;
  i0 = 255u;
  l18 = i0;
  i0 = l17;
  i1 = l18;
  i0 &= i1;
  l19 = i0;
  i0 = l10;
  l20 = i0;
  i0 = l19;
  l21 = i0;
  i0 = l20;
  i1 = l21;
  i0 = i0 != i1;
  l22 = i0;
  i0 = l22;
  l23 = i0;
  i0 = l23;
  i0 = !(i0);
  if (i0) {goto B2;}
  i0 = 112u;
  l24 = i0;
  i0 = l2;
  i1 = l24;
  i32_store((&memory), (u64)(i0 + 24), i1);
  goto B0;
  B2:;
  i0 = 0u;
  l25 = i0;
  i0 = 2u;
  l26 = i0;
  i0 = l2;
  i0 = i32_load((&memory), (u64)(i0 + 20));
  l27 = i0;
  i0 = l27;
  i0 = i32_load8_u((&memory), (u64)(i0 + 1));
  l28 = i0;
  i0 = l2;
  i0 = i32_load((&memory), (u64)(i0 + 12));
  l29 = i0;
  i0 = l29;
  i1 = l28;
  i32_store8((&memory), (u64)(i0), i1);
  i0 = l2;
  i0 = i32_load((&memory), (u64)(i0 + 8));
  l30 = i0;
  i0 = l30;
  i1 = l26;
  i32_store((&memory), (u64)(i0), i1);
  i0 = l2;
  i1 = l25;
  i32_store((&memory), (u64)(i0 + 24), i1);
  B0:;
  i0 = l2;
  i0 = i32_load((&memory), (u64)(i0 + 24));
  l31 = i0;
  i0 = l31;
  goto Bfunc;
  Bfunc:;
  FUNC_EPILOGUE;
  return i0;
}

static u32 f3(u32 p0, u32 p1, u32 p2, u32 p3) {
  u32 l0 = 0, l1 = 0, l2 = 0, l3 = 0, l4 = 0, l5 = 0, l6 = 0, l7 = 0, 
      l8 = 0, l9 = 0, l10 = 0, l11 = 0, l12 = 0, l13 = 0, l14 = 0, l15 = 0, 
      l16 = 0, l17 = 0, l18 = 0, l19 = 0, l20 = 0, l21 = 0, l22 = 0, l23 = 0, 
      l24 = 0, l25 = 0, l26 = 0, l27 = 0, l28 = 0, l29 = 0, l30 = 0, l31 = 0, 
      l32 = 0, l33 = 0, l34 = 0, l35 = 0;
  FUNC_PROLOGUE;
  u32 i0, i1;
  i0 = g0;
  l0 = i0;
  i0 = 32u;
  l1 = i0;
  i0 = l0;
  i1 = l1;
  i0 -= i1;
  l2 = i0;
  i0 = 2u;
  l3 = i0;
  i0 = l2;
  i1 = p0;
  i32_store((&memory), (u64)(i0 + 20), i1);
  i0 = l2;
  i1 = p1;
  i32_store((&memory), (u64)(i0 + 16), i1);
  i0 = l2;
  i1 = p2;
  i32_store((&memory), (u64)(i0 + 12), i1);
  i0 = l2;
  i1 = p3;
  i32_store((&memory), (u64)(i0 + 8), i1);
  i0 = l2;
  i0 = i32_load((&memory), (u64)(i0 + 16));
  l4 = i0;
  i0 = l3;
  l5 = i0;
  i0 = l4;
  l6 = i0;
  i0 = l5;
  i1 = l6;
  i0 = i0 > i1;
  l7 = i0;
  i0 = l7;
  l8 = i0;
  i0 = l8;
  i0 = !(i0);
  if (i0) {goto B1;}
  i0 = 105u;
  l9 = i0;
  i0 = l2;
  i1 = l9;
  i32_store((&memory), (u64)(i0 + 24), i1);
  goto B0;
  B1:;
  i0 = 1u;
  l10 = i0;
  i0 = l2;
  i0 = i32_load((&memory), (u64)(i0 + 20));
  l11 = i0;
  i0 = l11;
  i0 = i32_load8_u((&memory), (u64)(i0));
  l12 = i0;
  i0 = l2;
  i1 = l12;
  i32_store8((&memory), (u64)(i0 + 31), i1);
  i0 = l2;
  i0 = i32_load8_u((&memory), (u64)(i0 + 31));
  l13 = i0;
  i0 = 255u;
  l14 = i0;
  i0 = l13;
  i1 = l14;
  i0 &= i1;
  l15 = i0;
  i0 = 15u;
  l16 = i0;
  i0 = l15;
  i1 = l16;
  i0 &= i1;
  l17 = i0;
  i0 = 255u;
  l18 = i0;
  i0 = l17;
  i1 = l18;
  i0 &= i1;
  l19 = i0;
  i0 = l10;
  l20 = i0;
  i0 = l19;
  l21 = i0;
  i0 = l20;
  i1 = l21;
  i0 = i0 != i1;
  l22 = i0;
  i0 = l22;
  l23 = i0;
  i0 = l23;
  i0 = !(i0);
  if (i0) {goto B2;}
  i0 = 112u;
  l24 = i0;
  i0 = l2;
  i1 = l24;
  i32_store((&memory), (u64)(i0 + 24), i1);
  goto B0;
  B2:;
  i0 = 0u;
  l25 = i0;
  i0 = 2u;
  l26 = i0;
  i0 = l2;
  i0 = i32_load((&memory), (u64)(i0 + 20));
  l27 = i0;
  i0 = l27;
  i0 = i32_load8_u((&memory), (u64)(i0 + 1));
  l28 = i0;
  i0 = 255u;
  l29 = i0;
  i0 = l28;
  i1 = l29;
  i0 &= i1;
  l30 = i0;
  i0 = 4294967295u;
  l31 = i0;
  i0 = l30;
  i1 = l31;
  i0 ^= i1;
  l32 = i0;
  i0 = l2;
  i0 = i32_load((&memory), (u64)(i0 + 12));
  l33 = i0;
  i0 = l33;
  i1 = l32;
  i32_store8((&memory), (u64)(i0), i1);
  i0 = l2;
  i0 = i32_load((&memory), (u64)(i0 + 8));
  l34 = i0;
  i0 = l34;
  i1 = l26;
  i32_store((&memory), (u64)(i0), i1);
  i0 = l2;
  i1 = l25;
  i32_store((&memory), (u64)(i0 + 24), i1);
  B0:;
  i0 = l2;
  i0 = i32_load((&memory), (u64)(i0 + 24));
  l35 = i0;
  i0 = l35;
  goto Bfunc;
  Bfunc:;
  FUNC_EPILOGUE;
  return i0;
}

static u32 f4(u32 p0, u32 p1, u32 p2, u32 p3) {
  u32 l0 = 0, l1 = 0, l2 = 0, l3 = 0, l4 = 0, l5 = 0, l6 = 0, l7 = 0, 
      l8 = 0, l9 = 0, l10 = 0, l11 = 0, l12 = 0, l13 = 0, l14 = 0, l15 = 0, 
      l16 = 0, l17 = 0, l18 = 0, l19 = 0, l20 = 0, l21 = 0, l22 = 0, l23 = 0, 
      l24 = 0, l25 = 0, l26 = 0, l27 = 0, l28 = 0, l29 = 0, l30 = 0, l31 = 0, 
      l32 = 0, l33 = 0, l34 = 0, l35 = 0, l36 = 0, l37 = 0, l38 = 0;
  FUNC_PROLOGUE;
  u32 i0, i1;
  i0 = g0;
  l0 = i0;
  i0 = 32u;
  l1 = i0;
  i0 = l0;
  i1 = l1;
  i0 -= i1;
  l2 = i0;
  i0 = 3u;
  l3 = i0;
  i0 = l2;
  i1 = p0;
  i32_store((&memory), (u64)(i0 + 20), i1);
  i0 = l2;
  i1 = p1;
  i32_store((&memory), (u64)(i0 + 16), i1);
  i0 = l2;
  i1 = p2;
  i32_store((&memory), (u64)(i0 + 12), i1);
  i0 = l2;
  i1 = p3;
  i32_store((&memory), (u64)(i0 + 8), i1);
  i0 = l2;
  i0 = i32_load((&memory), (u64)(i0 + 16));
  l4 = i0;
  i0 = l3;
  l5 = i0;
  i0 = l4;
  l6 = i0;
  i0 = l5;
  i1 = l6;
  i0 = i0 > i1;
  l7 = i0;
  i0 = l7;
  l8 = i0;
  i0 = l8;
  i0 = !(i0);
  if (i0) {goto B1;}
  i0 = 105u;
  l9 = i0;
  i0 = l2;
  i1 = l9;
  i32_store((&memory), (u64)(i0 + 24), i1);
  goto B0;
  B1:;
  i0 = 2u;
  l10 = i0;
  i0 = l2;
  i0 = i32_load((&memory), (u64)(i0 + 20));
  l11 = i0;
  i0 = l11;
  i0 = i32_load8_u((&memory), (u64)(i0));
  l12 = i0;
  i0 = l2;
  i1 = l12;
  i32_store8((&memory), (u64)(i0 + 31), i1);
  i0 = l2;
  i0 = i32_load8_u((&memory), (u64)(i0 + 31));
  l13 = i0;
  i0 = 255u;
  l14 = i0;
  i0 = l13;
  i1 = l14;
  i0 &= i1;
  l15 = i0;
  i0 = 15u;
  l16 = i0;
  i0 = l15;
  i1 = l16;
  i0 &= i1;
  l17 = i0;
  i0 = 255u;
  l18 = i0;
  i0 = l17;
  i1 = l18;
  i0 &= i1;
  l19 = i0;
  i0 = l10;
  l20 = i0;
  i0 = l19;
  l21 = i0;
  i0 = l20;
  i1 = l21;
  i0 = i0 != i1;
  l22 = i0;
  i0 = l22;
  l23 = i0;
  i0 = l23;
  i0 = !(i0);
  if (i0) {goto B2;}
  i0 = 112u;
  l24 = i0;
  i0 = l2;
  i1 = l24;
  i32_store((&memory), (u64)(i0 + 24), i1);
  goto B0;
  B2:;
  i0 = 0u;
  l25 = i0;
  i0 = 3u;
  l26 = i0;
  i0 = l2;
  i0 = i32_load((&memory), (u64)(i0 + 20));
  l27 = i0;
  i0 = l27;
  i0 = i32_load8_u((&memory), (u64)(i0 + 1));
  l28 = i0;
  i0 = 255u;
  l29 = i0;
  i0 = l28;
  i1 = l29;
  i0 &= i1;
  l30 = i0;
  i0 = l2;
  i0 = i32_load((&memory), (u64)(i0 + 20));
  l31 = i0;
  i0 = l31;
  i0 = i32_load8_u((&memory), (u64)(i0 + 2));
  l32 = i0;
  i0 = 255u;
  l33 = i0;
  i0 = l32;
  i1 = l33;
  i0 &= i1;
  l34 = i0;
  i0 = l30;
  i1 = l34;
  i0 ^= i1;
  l35 = i0;
  i0 = l2;
  i0 = i32_load((&memory), (u64)(i0 + 12));
  l36 = i0;
  i0 = l36;
  i1 = l35;
  i32_store8((&memory), (u64)(i0), i1);
  i0 = l2;
  i0 = i32_load((&memory), (u64)(i0 + 8));
  l37 = i0;
  i0 = l37;
  i1 = l26;
  i32_store((&memory), (u64)(i0), i1);
  i0 = l2;
  i1 = l25;
  i32_store((&memory), (u64)(i0 + 24), i1);
  B0:;
  i0 = l2;
  i0 = i32_load((&memory), (u64)(i0 + 24));
  l38 = i0;
  i0 = l38;
  goto Bfunc;
  Bfunc:;
  FUNC_EPILOGUE;
  return i0;
}

static u32 f5(u32 p0, u32 p1, u32 p2, u32 p3) {
  u32 l0 = 0, l1 = 0, l2 = 0, l3 = 0, l4 = 0, l5 = 0, l6 = 0, l7 = 0, 
      l8 = 0, l9 = 0, l10 = 0, l11 = 0, l12 = 0, l13 = 0, l14 = 0, l15 = 0, 
      l16 = 0, l17 = 0, l18 = 0, l19 = 0, l20 = 0, l21 = 0, l22 = 0, l23 = 0, 
      l24 = 0, l25 = 0, l26 = 0, l27 = 0, l28 = 0, l29 = 0, l30 = 0, l31 = 0, 
      l32 = 0, l33 = 0, l34 = 0, l35 = 0, l36 = 0, l37 = 0, l38 = 0;
  FUNC_PROLOGUE;
  u32 i0, i1;
  i0 = g0;
  l0 = i0;
  i0 = 32u;
  l1 = i0;
  i0 = l0;
  i1 = l1;
  i0 -= i1;
  l2 = i0;
  i0 = 3u;
  l3 = i0;
  i0 = l2;
  i1 = p0;
  i32_store((&memory), (u64)(i0 + 20), i1);
  i0 = l2;
  i1 = p1;
  i32_store((&memory), (u64)(i0 + 16), i1);
  i0 = l2;
  i1 = p2;
  i32_store((&memory), (u64)(i0 + 12), i1);
  i0 = l2;
  i1 = p3;
  i32_store((&memory), (u64)(i0 + 8), i1);
  i0 = l2;
  i0 = i32_load((&memory), (u64)(i0 + 16));
  l4 = i0;
  i0 = l3;
  l5 = i0;
  i0 = l4;
  l6 = i0;
  i0 = l5;
  i1 = l6;
  i0 = i0 > i1;
  l7 = i0;
  i0 = l7;
  l8 = i0;
  i0 = l8;
  i0 = !(i0);
  if (i0) {goto B1;}
  i0 = 105u;
  l9 = i0;
  i0 = l2;
  i1 = l9;
  i32_store((&memory), (u64)(i0 + 24), i1);
  goto B0;
  B1:;
  i0 = 3u;
  l10 = i0;
  i0 = l2;
  i0 = i32_load((&memory), (u64)(i0 + 20));
  l11 = i0;
  i0 = l11;
  i0 = i32_load8_u((&memory), (u64)(i0));
  l12 = i0;
  i0 = l2;
  i1 = l12;
  i32_store8((&memory), (u64)(i0 + 31), i1);
  i0 = l2;
  i0 = i32_load8_u((&memory), (u64)(i0 + 31));
  l13 = i0;
  i0 = 255u;
  l14 = i0;
  i0 = l13;
  i1 = l14;
  i0 &= i1;
  l15 = i0;
  i0 = 15u;
  l16 = i0;
  i0 = l15;
  i1 = l16;
  i0 &= i1;
  l17 = i0;
  i0 = 255u;
  l18 = i0;
  i0 = l17;
  i1 = l18;
  i0 &= i1;
  l19 = i0;
  i0 = l10;
  l20 = i0;
  i0 = l19;
  l21 = i0;
  i0 = l20;
  i1 = l21;
  i0 = i0 != i1;
  l22 = i0;
  i0 = l22;
  l23 = i0;
  i0 = l23;
  i0 = !(i0);
  if (i0) {goto B2;}
  i0 = 112u;
  l24 = i0;
  i0 = l2;
  i1 = l24;
  i32_store((&memory), (u64)(i0 + 24), i1);
  goto B0;
  B2:;
  i0 = 0u;
  l25 = i0;
  i0 = 3u;
  l26 = i0;
  i0 = l2;
  i0 = i32_load((&memory), (u64)(i0 + 20));
  l27 = i0;
  i0 = l27;
  i0 = i32_load8_u((&memory), (u64)(i0 + 1));
  l28 = i0;
  i0 = 255u;
  l29 = i0;
  i0 = l28;
  i1 = l29;
  i0 &= i1;
  l30 = i0;
  i0 = l2;
  i0 = i32_load((&memory), (u64)(i0 + 20));
  l31 = i0;
  i0 = l31;
  i0 = i32_load8_u((&memory), (u64)(i0 + 2));
  l32 = i0;
  i0 = 255u;
  l33 = i0;
  i0 = l32;
  i1 = l33;
  i0 &= i1;
  l34 = i0;
  i0 = l30;
  i1 = l34;
  i0 &= i1;
  l35 = i0;
  i0 = l2;
  i0 = i32_load((&memory), (u64)(i0 + 12));
  l36 = i0;
  i0 = l36;
  i1 = l35;
  i32_store8((&memory), (u64)(i0), i1);
  i0 = l2;
  i0 = i32_load((&memory), (u64)(i0 + 8));
  l37 = i0;
  i0 = l37;
  i1 = l26;
  i32_store((&memory), (u64)(i0), i1);
  i0 = l2;
  i1 = l25;
  i32_store((&memory), (u64)(i0 + 24), i1);
  B0:;
  i0 = l2;
  i0 = i32_load((&memory), (u64)(i0 + 24));
  l38 = i0;
  i0 = l38;
  goto Bfunc;
  Bfunc:;
  FUNC_EPILOGUE;
  return i0;
}

static u32 f6(u32 p0, u32 p1, u32 p2, u32 p3) {
  u32 l0 = 0, l1 = 0, l2 = 0, l3 = 0, l4 = 0, l5 = 0, l6 = 0, l7 = 0, 
      l8 = 0, l9 = 0, l10 = 0, l11 = 0, l12 = 0, l13 = 0, l14 = 0, l15 = 0, 
      l16 = 0, l17 = 0, l18 = 0, l19 = 0, l20 = 0, l21 = 0, l22 = 0, l23 = 0, 
      l24 = 0, l25 = 0, l26 = 0, l27 = 0, l28 = 0, l29 = 0, l30 = 0, l31 = 0, 
      l32 = 0, l33 = 0, l34 = 0, l35 = 0, l36 = 0, l37 = 0, l38 = 0;
  FUNC_PROLOGUE;
  u32 i0, i1;
  i0 = g0;
  l0 = i0;
  i0 = 32u;
  l1 = i0;
  i0 = l0;
  i1 = l1;
  i0 -= i1;
  l2 = i0;
  i0 = 3u;
  l3 = i0;
  i0 = l2;
  i1 = p0;
  i32_store((&memory), (u64)(i0 + 20), i1);
  i0 = l2;
  i1 = p1;
  i32_store((&memory), (u64)(i0 + 16), i1);
  i0 = l2;
  i1 = p2;
  i32_store((&memory), (u64)(i0 + 12), i1);
  i0 = l2;
  i1 = p3;
  i32_store((&memory), (u64)(i0 + 8), i1);
  i0 = l2;
  i0 = i32_load((&memory), (u64)(i0 + 16));
  l4 = i0;
  i0 = l3;
  l5 = i0;
  i0 = l4;
  l6 = i0;
  i0 = l5;
  i1 = l6;
  i0 = i0 > i1;
  l7 = i0;
  i0 = l7;
  l8 = i0;
  i0 = l8;
  i0 = !(i0);
  if (i0) {goto B1;}
  i0 = 105u;
  l9 = i0;
  i0 = l2;
  i1 = l9;
  i32_store((&memory), (u64)(i0 + 24), i1);
  goto B0;
  B1:;
  i0 = 4u;
  l10 = i0;
  i0 = l2;
  i0 = i32_load((&memory), (u64)(i0 + 20));
  l11 = i0;
  i0 = l11;
  i0 = i32_load8_u((&memory), (u64)(i0));
  l12 = i0;
  i0 = l2;
  i1 = l12;
  i32_store8((&memory), (u64)(i0 + 31), i1);
  i0 = l2;
  i0 = i32_load8_u((&memory), (u64)(i0 + 31));
  l13 = i0;
  i0 = 255u;
  l14 = i0;
  i0 = l13;
  i1 = l14;
  i0 &= i1;
  l15 = i0;
  i0 = 15u;
  l16 = i0;
  i0 = l15;
  i1 = l16;
  i0 &= i1;
  l17 = i0;
  i0 = 255u;
  l18 = i0;
  i0 = l17;
  i1 = l18;
  i0 &= i1;
  l19 = i0;
  i0 = l10;
  l20 = i0;
  i0 = l19;
  l21 = i0;
  i0 = l20;
  i1 = l21;
  i0 = i0 != i1;
  l22 = i0;
  i0 = l22;
  l23 = i0;
  i0 = l23;
  i0 = !(i0);
  if (i0) {goto B2;}
  i0 = 112u;
  l24 = i0;
  i0 = l2;
  i1 = l24;
  i32_store((&memory), (u64)(i0 + 24), i1);
  goto B0;
  B2:;
  i0 = 0u;
  l25 = i0;
  i0 = 3u;
  l26 = i0;
  i0 = l2;
  i0 = i32_load((&memory), (u64)(i0 + 20));
  l27 = i0;
  i0 = l27;
  i0 = i32_load8_u((&memory), (u64)(i0 + 1));
  l28 = i0;
  i0 = 255u;
  l29 = i0;
  i0 = l28;
  i1 = l29;
  i0 &= i1;
  l30 = i0;
  i0 = l2;
  i0 = i32_load((&memory), (u64)(i0 + 20));
  l31 = i0;
  i0 = l31;
  i0 = i32_load8_u((&memory), (u64)(i0 + 2));
  l32 = i0;
  i0 = 255u;
  l33 = i0;
  i0 = l32;
  i1 = l33;
  i0 &= i1;
  l34 = i0;
  i0 = l30;
  i1 = l34;
  i0 |= i1;
  l35 = i0;
  i0 = l2;
  i0 = i32_load((&memory), (u64)(i0 + 12));
  l36 = i0;
  i0 = l36;
  i1 = l35;
  i32_store8((&memory), (u64)(i0), i1);
  i0 = l2;
  i0 = i32_load((&memory), (u64)(i0 + 8));
  l37 = i0;
  i0 = l37;
  i1 = l26;
  i32_store((&memory), (u64)(i0), i1);
  i0 = l2;
  i1 = l25;
  i32_store((&memory), (u64)(i0 + 24), i1);
  B0:;
  i0 = l2;
  i0 = i32_load((&memory), (u64)(i0 + 24));
  l38 = i0;
  i0 = l38;
  goto Bfunc;
  Bfunc:;
  FUNC_EPILOGUE;
  return i0;
}

static u32 f7(u32 p0, u32 p1, u32 p2, u32 p3) {
  u32 l0 = 0, l1 = 0, l2 = 0, l3 = 0, l4 = 0, l5 = 0, l6 = 0, l7 = 0, 
      l8 = 0, l9 = 0, l10 = 0, l11 = 0, l12 = 0, l13 = 0, l14 = 0, l15 = 0, 
      l16 = 0, l17 = 0, l18 = 0, l19 = 0, l20 = 0, l21 = 0, l22 = 0, l23 = 0, 
      l24 = 0, l25 = 0, l26 = 0, l27 = 0, l28 = 0, l29 = 0, l30 = 0, l31 = 0, 
      l32 = 0, l33 = 0, l34 = 0, l35 = 0, l36 = 0, l37 = 0, l38 = 0;
  FUNC_PROLOGUE;
  u32 i0, i1;
  i0 = g0;
  l0 = i0;
  i0 = 32u;
  l1 = i0;
  i0 = l0;
  i1 = l1;
  i0 -= i1;
  l2 = i0;
  i0 = 3u;
  l3 = i0;
  i0 = l2;
  i1 = p0;
  i32_store((&memory), (u64)(i0 + 20), i1);
  i0 = l2;
  i1 = p1;
  i32_store((&memory), (u64)(i0 + 16), i1);
  i0 = l2;
  i1 = p2;
  i32_store((&memory), (u64)(i0 + 12), i1);
  i0 = l2;
  i1 = p3;
  i32_store((&memory), (u64)(i0 + 8), i1);
  i0 = l2;
  i0 = i32_load((&memory), (u64)(i0 + 16));
  l4 = i0;
  i0 = l3;
  l5 = i0;
  i0 = l4;
  l6 = i0;
  i0 = l5;
  i1 = l6;
  i0 = i0 > i1;
  l7 = i0;
  i0 = l7;
  l8 = i0;
  i0 = l8;
  i0 = !(i0);
  if (i0) {goto B1;}
  i0 = 105u;
  l9 = i0;
  i0 = l2;
  i1 = l9;
  i32_store((&memory), (u64)(i0 + 24), i1);
  goto B0;
  B1:;
  i0 = 5u;
  l10 = i0;
  i0 = l2;
  i0 = i32_load((&memory), (u64)(i0 + 20));
  l11 = i0;
  i0 = l11;
  i0 = i32_load8_u((&memory), (u64)(i0));
  l12 = i0;
  i0 = l2;
  i1 = l12;
  i32_store8((&memory), (u64)(i0 + 31), i1);
  i0 = l2;
  i0 = i32_load8_u((&memory), (u64)(i0 + 31));
  l13 = i0;
  i0 = 255u;
  l14 = i0;
  i0 = l13;
  i1 = l14;
  i0 &= i1;
  l15 = i0;
  i0 = 15u;
  l16 = i0;
  i0 = l15;
  i1 = l16;
  i0 &= i1;
  l17 = i0;
  i0 = 255u;
  l18 = i0;
  i0 = l17;
  i1 = l18;
  i0 &= i1;
  l19 = i0;
  i0 = l10;
  l20 = i0;
  i0 = l19;
  l21 = i0;
  i0 = l20;
  i1 = l21;
  i0 = i0 != i1;
  l22 = i0;
  i0 = l22;
  l23 = i0;
  i0 = l23;
  i0 = !(i0);
  if (i0) {goto B2;}
  i0 = 112u;
  l24 = i0;
  i0 = l2;
  i1 = l24;
  i32_store((&memory), (u64)(i0 + 24), i1);
  goto B0;
  B2:;
  i0 = 0u;
  l25 = i0;
  i0 = 3u;
  l26 = i0;
  i0 = l2;
  i0 = i32_load((&memory), (u64)(i0 + 20));
  l27 = i0;
  i0 = l27;
  i0 = i32_load8_u((&memory), (u64)(i0 + 1));
  l28 = i0;
  i0 = 255u;
  l29 = i0;
  i0 = l28;
  i1 = l29;
  i0 &= i1;
  l30 = i0;
  i0 = l2;
  i0 = i32_load((&memory), (u64)(i0 + 20));
  l31 = i0;
  i0 = l31;
  i0 = i32_load8_u((&memory), (u64)(i0 + 2));
  l32 = i0;
  i0 = 255u;
  l33 = i0;
  i0 = l32;
  i1 = l33;
  i0 &= i1;
  l34 = i0;
  i0 = l30;
  i1 = l34;
  i0 += i1;
  l35 = i0;
  i0 = l2;
  i0 = i32_load((&memory), (u64)(i0 + 12));
  l36 = i0;
  i0 = l36;
  i1 = l35;
  i32_store8((&memory), (u64)(i0), i1);
  i0 = l2;
  i0 = i32_load((&memory), (u64)(i0 + 8));
  l37 = i0;
  i0 = l37;
  i1 = l26;
  i32_store((&memory), (u64)(i0), i1);
  i0 = l2;
  i1 = l25;
  i32_store((&memory), (u64)(i0 + 24), i1);
  B0:;
  i0 = l2;
  i0 = i32_load((&memory), (u64)(i0 + 24));
  l38 = i0;
  i0 = l38;
  goto Bfunc;
  Bfunc:;
  FUNC_EPILOGUE;
  return i0;
}

static u32 f8(u32 p0, u32 p1, u32 p2, u32 p3) {
  u32 l0 = 0, l1 = 0, l2 = 0, l3 = 0, l4 = 0, l5 = 0, l6 = 0, l7 = 0, 
      l8 = 0, l9 = 0, l10 = 0, l11 = 0, l12 = 0, l13 = 0, l14 = 0, l15 = 0, 
      l16 = 0, l17 = 0, l18 = 0, l19 = 0, l20 = 0, l21 = 0, l22 = 0, l23 = 0, 
      l24 = 0, l25 = 0, l26 = 0, l27 = 0, l28 = 0, l29 = 0, l30 = 0, l31 = 0, 
      l32 = 0, l33 = 0, l34 = 0, l35 = 0, l36 = 0, l37 = 0, l38 = 0, l39 = 0, 
      l40 = 0;
  FUNC_PROLOGUE;
  u32 i0, i1;
  i0 = g0;
  l0 = i0;
  i0 = 32u;
  l1 = i0;
  i0 = l0;
  i1 = l1;
  i0 -= i1;
  l2 = i0;
  i0 = 3u;
  l3 = i0;
  i0 = l2;
  i1 = p0;
  i32_store((&memory), (u64)(i0 + 20), i1);
  i0 = l2;
  i1 = p1;
  i32_store((&memory), (u64)(i0 + 16), i1);
  i0 = l2;
  i1 = p2;
  i32_store((&memory), (u64)(i0 + 12), i1);
  i0 = l2;
  i1 = p3;
  i32_store((&memory), (u64)(i0 + 8), i1);
  i0 = l2;
  i0 = i32_load((&memory), (u64)(i0 + 16));
  l4 = i0;
  i0 = l3;
  l5 = i0;
  i0 = l4;
  l6 = i0;
  i0 = l5;
  i1 = l6;
  i0 = i0 > i1;
  l7 = i0;
  i0 = l7;
  l8 = i0;
  i0 = l8;
  i0 = !(i0);
  if (i0) {goto B1;}
  i0 = 105u;
  l9 = i0;
  i0 = l2;
  i1 = l9;
  i32_store((&memory), (u64)(i0 + 24), i1);
  goto B0;
  B1:;
  i0 = 6u;
  l10 = i0;
  i0 = l2;
  i0 = i32_load((&memory), (u64)(i0 + 20));
  l11 = i0;
  i0 = l11;
  i0 = i32_load8_u((&memory), (u64)(i0));
  l12 = i0;
  i0 = l2;
  i1 = l12;
  i32_store8((&memory), (u64)(i0 + 31), i1);
  i0 = l2;
  i0 = i32_load8_u((&memory), (u64)(i0 + 31));
  l13 = i0;
  i0 = 255u;
  l14 = i0;
  i0 = l13;
  i1 = l14;
  i0 &= i1;
  l15 = i0;
  i0 = 15u;
  l16 = i0;
  i0 = l15;
  i1 = l16;
  i0 &= i1;
  l17 = i0;
  i0 = 255u;
  l18 = i0;
  i0 = l17;
  i1 = l18;
  i0 &= i1;
  l19 = i0;
  i0 = l10;
  l20 = i0;
  i0 = l19;
  l21 = i0;
  i0 = l20;
  i1 = l21;
  i0 = i0 != i1;
  l22 = i0;
  i0 = l22;
  l23 = i0;
  i0 = l23;
  i0 = !(i0);
  if (i0) {goto B2;}
  i0 = 112u;
  l24 = i0;
  i0 = l2;
  i1 = l24;
  i32_store((&memory), (u64)(i0 + 24), i1);
  goto B0;
  B2:;
  i0 = 0u;
  l25 = i0;
  i0 = 3u;
  l26 = i0;
  i0 = l2;
  i0 = i32_load((&memory), (u64)(i0 + 20));
  l27 = i0;
  i0 = l27;
  i0 = i32_load8_u((&memory), (u64)(i0 + 2));
  l28 = i0;
  i0 = 255u;
  l29 = i0;
  i0 = l28;
  i1 = l29;
  i0 &= i1;
  l30 = i0;
  i0 = l2;
  i0 = i32_load((&memory), (u64)(i0 + 20));
  l31 = i0;
  i0 = l31;
  i0 = i32_load8_u((&memory), (u64)(i0 + 1));
  l32 = i0;
  i0 = 255u;
  l33 = i0;
  i0 = l32;
  i1 = l33;
  i0 &= i1;
  l34 = i0;
  i0 = l30;
  i1 = l34;
  i0 -= i1;
  l35 = i0;
  i0 = 255u;
  l36 = i0;
  i0 = l35;
  i1 = l36;
  i0 &= i1;
  l37 = i0;
  i0 = l2;
  i0 = i32_load((&memory), (u64)(i0 + 12));
  l38 = i0;
  i0 = l38;
  i1 = l37;
  i32_store8((&memory), (u64)(i0), i1);
  i0 = l2;
  i0 = i32_load((&memory), (u64)(i0 + 8));
  l39 = i0;
  i0 = l39;
  i1 = l26;
  i32_store((&memory), (u64)(i0), i1);
  i0 = l2;
  i1 = l25;
  i32_store((&memory), (u64)(i0 + 24), i1);
  B0:;
  i0 = l2;
  i0 = i32_load((&memory), (u64)(i0 + 24));
  l40 = i0;
  i0 = l40;
  goto Bfunc;
  Bfunc:;
  FUNC_EPILOGUE;
  return i0;
}

static u32 f9(u32 p0, u32 p1, u32 p2, u32 p3, u32 p4) {
  u32 l0 = 0, l1 = 0, l2 = 0, l3 = 0, l4 = 0, l5 = 0, l6 = 0, l7 = 0, 
      l8 = 0, l9 = 0, l10 = 0, l11 = 0, l12 = 0, l13 = 0, l14 = 0, l15 = 0, 
      l16 = 0, l17 = 0, l18 = 0, l19 = 0, l20 = 0, l21 = 0, l22 = 0, l23 = 0, 
      l24 = 0, l25 = 0, l26 = 0, l27 = 0, l28 = 0, l29 = 0, l30 = 0, l31 = 0, 
      l32 = 0, l33 = 0, l34 = 0, l35 = 0, l36 = 0, l37 = 0, l38 = 0, l39 = 0, 
      l40 = 0, l41 = 0, l42 = 0, l43 = 0, l44 = 0, l45 = 0, l46 = 0, l47 = 0, 
      l48 = 0, l49 = 0, l50 = 0, l51 = 0, l52 = 0, l53 = 0, l54 = 0, l55 = 0, 
      l56 = 0, l57 = 0, l58 = 0, l59 = 0, l60 = 0, l61 = 0, l62 = 0, l63 = 0, 
      l64 = 0, l65 = 0, l66 = 0, l67 = 0, l68 = 0, l69 = 0, l70 = 0, l71 = 0, 
      l72 = 0, l73 = 0, l74 = 0, l75 = 0, l76 = 0, l77 = 0, l78 = 0, l79 = 0, 
      l80 = 0, l81 = 0, l82 = 0, l83 = 0, l84 = 0, l85 = 0, l86 = 0, l87 = 0, 
      l88 = 0, l89 = 0, l90 = 0, l91 = 0, l92 = 0, l93 = 0, l94 = 0, l95 = 0, 
      l96 = 0, l97 = 0, l98 = 0, l99 = 0, l100 = 0, l101 = 0, l102 = 0, l103 = 0, 
      l104 = 0, l105 = 0, l106 = 0, l107 = 0, l108 = 0, l109 = 0, l110 = 0, l111 = 0, 
      l112 = 0, l113 = 0;
  FUNC_PROLOGUE;
  u32 i0, i1, i2, i3, i4;
  i0 = g0;
  l0 = i0;
  i0 = 64u;
  l1 = i0;
  i0 = l0;
  i1 = l1;
  i0 -= i1;
  l2 = i0;
  i0 = l2;
  g0 = i0;
  i0 = 0u;
  l3 = i0;
  i0 = l2;
  i1 = p0;
  i32_store((&memory), (u64)(i0 + 52), i1);
  i0 = l2;
  i1 = p1;
  i32_store((&memory), (u64)(i0 + 48), i1);
  i0 = l2;
  i1 = p2;
  i32_store((&memory), (u64)(i0 + 44), i1);
  i0 = l2;
  i1 = p3;
  i32_store((&memory), (u64)(i0 + 40), i1);
  i0 = l2;
  i1 = p4;
  i32_store((&memory), (u64)(i0 + 36), i1);
  i0 = l2;
  i1 = l3;
  i32_store((&memory), (u64)(i0 + 32), i1);
  i0 = l2;
  i0 = i32_load((&memory), (u64)(i0 + 52));
  l4 = i0;
  i0 = l2;
  i1 = l4;
  i32_store((&memory), (u64)(i0 + 28), i1);
  i0 = l2;
  i1 = l3;
  i32_store((&memory), (u64)(i0 + 24), i1);
  L1: 
    i0 = 0u;
    l5 = i0;
    i0 = l2;
    i0 = i32_load((&memory), (u64)(i0 + 28));
    l6 = i0;
    i0 = l2;
    i0 = i32_load((&memory), (u64)(i0 + 52));
    l7 = i0;
    i0 = l2;
    i0 = i32_load((&memory), (u64)(i0 + 48));
    l8 = i0;
    i0 = l7;
    i1 = l8;
    i0 += i1;
    l9 = i0;
    i0 = l6;
    l10 = i0;
    i0 = l9;
    l11 = i0;
    i0 = l10;
    i1 = l11;
    i0 = i0 < i1;
    l12 = i0;
    i0 = l12;
    l13 = i0;
    i0 = l5;
    l14 = i0;
    i0 = l13;
    i0 = !(i0);
    if (i0) {goto B2;}
    i0 = l2;
    i0 = i32_load((&memory), (u64)(i0 + 24));
    l15 = i0;
    i0 = l2;
    i0 = i32_load((&memory), (u64)(i0 + 40));
    l16 = i0;
    i0 = l15;
    l17 = i0;
    i0 = l16;
    l18 = i0;
    i0 = l17;
    i1 = l18;
    i0 = i0 < i1;
    l19 = i0;
    i0 = l19;
    l14 = i0;
    B2:;
    i0 = l14;
    l20 = i0;
    i0 = 1u;
    l21 = i0;
    i0 = l20;
    i1 = l21;
    i0 &= i1;
    l22 = i0;
    i0 = l22;
    i0 = !(i0);
    if (i0) {goto B3;}
    i0 = 7u;
    l23 = i0;
    i0 = l2;
    i0 = i32_load((&memory), (u64)(i0 + 28));
    l24 = i0;
    i0 = l24;
    i0 = i32_load8_u((&memory), (u64)(i0));
    l25 = i0;
    i0 = l2;
    i1 = l25;
    i32_store8((&memory), (u64)(i0 + 63), i1);
    i0 = l2;
    i0 = i32_load8_u((&memory), (u64)(i0 + 63));
    l26 = i0;
    i0 = 255u;
    l27 = i0;
    i0 = l26;
    i1 = l27;
    i0 &= i1;
    l28 = i0;
    i0 = 15u;
    l29 = i0;
    i0 = l28;
    i1 = l29;
    i0 &= i1;
    l30 = i0;
    i0 = l2;
    i1 = l30;
    i32_store8((&memory), (u64)(i0 + 23), i1);
    i0 = l2;
    i0 = i32_load8_u((&memory), (u64)(i0 + 23));
    l31 = i0;
    i0 = 255u;
    l32 = i0;
    i0 = l31;
    i1 = l32;
    i0 &= i1;
    l33 = i0;
    i0 = l23;
    l34 = i0;
    i0 = l33;
    l35 = i0;
    i0 = l34;
    i1 = l35;
    i0 = (u32)((s32)i0 <= (s32)i1);
    l36 = i0;
    i0 = l36;
    l37 = i0;
    i0 = l37;
    i0 = !(i0);
    if (i0) {goto B4;}
    i0 = 112u;
    l38 = i0;
    i0 = l2;
    i1 = l38;
    i32_store((&memory), (u64)(i0 + 56), i1);
    goto B0;
    B4:;
    i0 = 0u;
    l39 = i0;
    i0 = 15u;
    l40 = i0;
    i0 = l2;
    i1 = l40;
    i0 += i1;
    l41 = i0;
    i0 = l41;
    l42 = i0;
    i0 = 8u;
    l43 = i0;
    i0 = l2;
    i1 = l43;
    i0 += i1;
    l44 = i0;
    i0 = l44;
    l45 = i0;
    i0 = 0u;
    l46 = i0;
    i0 = 1024u;
    l47 = i0;
    i0 = l2;
    i0 = i32_load8_u((&memory), (u64)(i0 + 23));
    l48 = i0;
    i0 = 255u;
    l49 = i0;
    i0 = l48;
    i1 = l49;
    i0 &= i1;
    l50 = i0;
    i0 = 2u;
    l51 = i0;
    i0 = l50;
    i1 = l51;
    i0 <<= (i1 & 31);
    l52 = i0;
    i0 = l47;
    i1 = l52;
    i0 += i1;
    l53 = i0;
    i0 = l53;
    i0 = i32_load((&memory), (u64)(i0));
    l54 = i0;
    i0 = l2;
    i1 = l54;
    i32_store((&memory), (u64)(i0 + 16), i1);
    i0 = l2;
    i1 = l46;
    i32_store8((&memory), (u64)(i0 + 15), i1);
    i0 = l2;
    i1 = l39;
    i32_store((&memory), (u64)(i0 + 8), i1);
    i0 = l2;
    i0 = i32_load((&memory), (u64)(i0 + 16));
    l55 = i0;
    i0 = l2;
    i0 = i32_load((&memory), (u64)(i0 + 28));
    l56 = i0;
    i0 = l2;
    i0 = i32_load((&memory), (u64)(i0 + 48));
    l57 = i0;
    i0 = l2;
    i0 = i32_load((&memory), (u64)(i0 + 28));
    l58 = i0;
    i0 = l2;
    i0 = i32_load((&memory), (u64)(i0 + 52));
    l59 = i0;
    i0 = l58;
    i1 = l59;
    i0 -= i1;
    l60 = i0;
    i0 = l57;
    i1 = l60;
    i0 -= i1;
    l61 = i0;
    i0 = l56;
    i1 = l61;
    i2 = l42;
    i3 = l45;
    i4 = l55;
    i0 = CALL_INDIRECT(T0, u32 (*)(u32, u32, u32, u32), 0, i4, i0, i1, i2, i3);
    l62 = i0;
    i0 = l39;
    l63 = i0;
    i0 = l62;
    l64 = i0;
    i0 = l63;
    i1 = l64;
    i0 = i0 != i1;
    l65 = i0;
    i0 = l65;
    l66 = i0;
    i0 = l66;
    i0 = !(i0);
    if (i0) {goto B5;}
    goto B3;
    B5:;
    i0 = l2;
    i0 = i32_load8_u((&memory), (u64)(i0 + 15));
    l67 = i0;
    i0 = 255u;
    l68 = i0;
    i0 = l67;
    i1 = l68;
    i0 &= i1;
    l69 = i0;
    i0 = l2;
    i0 = i32_load((&memory), (u64)(i0 + 44));
    l70 = i0;
    i0 = l2;
    i0 = i32_load((&memory), (u64)(i0 + 24));
    l71 = i0;
    i0 = l70;
    i1 = l71;
    i0 += i1;
    l72 = i0;
    i0 = l72;
    i0 = i32_load8_u((&memory), (u64)(i0));
    l73 = i0;
    i0 = 24u;
    l74 = i0;
    i0 = l73;
    i1 = l74;
    i0 <<= (i1 & 31);
    l75 = i0;
    i0 = l75;
    i1 = l74;
    i0 = (u32)((s32)i0 >> (i1 & 31));
    l76 = i0;
    i0 = l69;
    l77 = i0;
    i0 = l76;
    l78 = i0;
    i0 = l77;
    i1 = l78;
    i0 = i0 == i1;
    l79 = i0;
    i0 = l79;
    l80 = i0;
    i0 = l80;
    i0 = !(i0);
    if (i0) {goto B6;}
    i0 = l2;
    i0 = i32_load((&memory), (u64)(i0 + 32));
    l81 = i0;
    i0 = 1u;
    l82 = i0;
    i0 = l81;
    i1 = l82;
    i0 += i1;
    l83 = i0;
    i0 = l2;
    i1 = l83;
    i32_store((&memory), (u64)(i0 + 32), i1);
    B6:;
    i0 = l2;
    i0 = i32_load((&memory), (u64)(i0 + 8));
    l84 = i0;
    i0 = l2;
    i0 = i32_load((&memory), (u64)(i0 + 28));
    l85 = i0;
    i0 = l85;
    i1 = l84;
    i0 += i1;
    l86 = i0;
    i0 = l2;
    i1 = l86;
    i32_store((&memory), (u64)(i0 + 28), i1);
    i0 = l2;
    i0 = i32_load((&memory), (u64)(i0 + 24));
    l87 = i0;
    i0 = 1u;
    l88 = i0;
    i0 = l87;
    i1 = l88;
    i0 += i1;
    l89 = i0;
    i0 = l2;
    i1 = l89;
    i32_store((&memory), (u64)(i0 + 24), i1);
    goto L1;
    B3:;
  i0 = l2;
  i0 = i32_load((&memory), (u64)(i0 + 28));
  l90 = i0;
  i0 = l2;
  i0 = i32_load((&memory), (u64)(i0 + 52));
  l91 = i0;
  i0 = l2;
  i0 = i32_load((&memory), (u64)(i0 + 48));
  l92 = i0;
  i0 = l91;
  i1 = l92;
  i0 += i1;
  l93 = i0;
  i0 = l90;
  l94 = i0;
  i0 = l93;
  l95 = i0;
  i0 = l94;
  i1 = l95;
  i0 = i0 != i1;
  l96 = i0;
  i0 = l96;
  l97 = i0;
  i0 = l97;
  i0 = !(i0);
  if (i0) {goto B8;}
  i0 = 0u;
  l98 = i0;
  i0 = l2;
  i0 = i32_load((&memory), (u64)(i0 + 36));
  l99 = i0;
  i0 = l99;
  i1 = l98;
  i32_store8((&memory), (u64)(i0), i1);
  goto B7;
  B8:;
  i0 = l2;
  i0 = i32_load((&memory), (u64)(i0 + 32));
  l100 = i0;
  i0 = l2;
  i0 = i32_load((&memory), (u64)(i0 + 40));
  l101 = i0;
  i0 = l100;
  l102 = i0;
  i0 = l101;
  l103 = i0;
  i0 = l102;
  i1 = l103;
  i0 = i0 != i1;
  l104 = i0;
  i0 = l104;
  l105 = i0;
  i0 = l105;
  i0 = !(i0);
  if (i0) {goto B10;}
  i0 = 0u;
  l106 = i0;
  i0 = l2;
  i0 = i32_load((&memory), (u64)(i0 + 36));
  l107 = i0;
  i0 = l107;
  i1 = l106;
  i32_store8((&memory), (u64)(i0), i1);
  goto B9;
  B10:;
  i0 = 1u;
  l108 = i0;
  i0 = l2;
  i0 = i32_load((&memory), (u64)(i0 + 36));
  l109 = i0;
  i0 = l109;
  i1 = l108;
  i32_store8((&memory), (u64)(i0), i1);
  B9:;
  B7:;
  i0 = 0u;
  l110 = i0;
  i0 = l2;
  i1 = l110;
  i32_store((&memory), (u64)(i0 + 56), i1);
  B0:;
  i0 = l2;
  i0 = i32_load((&memory), (u64)(i0 + 56));
  l111 = i0;
  i0 = 64u;
  l112 = i0;
  i0 = l2;
  i1 = l112;
  i0 += i1;
  l113 = i0;
  i0 = l113;
  g0 = i0;
  i0 = l111;
  goto Bfunc;
  Bfunc:;
  FUNC_EPILOGUE;
  return i0;
}

static u32 Match(u32 p0, u32 p1, u32 p2, u32 p3) {
  u32 l0 = 0, l1 = 0, l2 = 0, l3 = 0, l4 = 0, l5 = 0, l6 = 0, l7 = 0, 
      l8 = 0, l9 = 0, l10 = 0, l11 = 0, l12 = 0, l13 = 0, l14 = 0, l15 = 0, 
      l16 = 0, l17 = 0, l18 = 0, l19 = 0, l20 = 0, l21 = 0, l22 = 0, l23 = 0;
  FUNC_PROLOGUE;
  u32 i0, i1, i2, i3, i4;
  i0 = g0;
  l0 = i0;
  i0 = 32u;
  l1 = i0;
  i0 = l0;
  i1 = l1;
  i0 -= i1;
  l2 = i0;
  i0 = l2;
  g0 = i0;
  i0 = 0u;
  l3 = i0;
  i0 = 11u;
  l4 = i0;
  i0 = l2;
  i1 = l4;
  i0 += i1;
  l5 = i0;
  i0 = l5;
  l6 = i0;
  i0 = 0u;
  l7 = i0;
  i0 = l2;
  i1 = p0;
  i32_store((&memory), (u64)(i0 + 24), i1);
  i0 = l2;
  i1 = p1;
  i32_store((&memory), (u64)(i0 + 20), i1);
  i0 = l2;
  i1 = p2;
  i32_store((&memory), (u64)(i0 + 16), i1);
  i0 = l2;
  i1 = p3;
  i32_store((&memory), (u64)(i0 + 12), i1);
  i0 = l2;
  i1 = l7;
  i32_store8((&memory), (u64)(i0 + 11), i1);
  i0 = l2;
  i0 = i32_load((&memory), (u64)(i0 + 24));
  l8 = i0;
  i0 = l2;
  i0 = i32_load((&memory), (u64)(i0 + 20));
  l9 = i0;
  i0 = l2;
  i0 = i32_load((&memory), (u64)(i0 + 16));
  l10 = i0;
  i0 = l2;
  i0 = i32_load((&memory), (u64)(i0 + 12));
  l11 = i0;
  i0 = l8;
  i1 = l9;
  i2 = l10;
  i3 = l11;
  i4 = l6;
  i0 = f9(i0, i1, i2, i3, i4);
  l12 = i0;
  i0 = l3;
  l13 = i0;
  i0 = l12;
  l14 = i0;
  i0 = l13;
  i1 = l14;
  i0 = i0 != i1;
  l15 = i0;
  i0 = l15;
  l16 = i0;
  i0 = l16;
  i0 = !(i0);
  if (i0) {goto B1;}
  i0 = 0u;
  l17 = i0;
  i0 = l2;
  i1 = l17;
  i32_store((&memory), (u64)(i0 + 28), i1);
  goto B0;
  B1:;
  i0 = l2;
  i0 = i32_load8_u((&memory), (u64)(i0 + 11));
  l18 = i0;
  i0 = 1u;
  l19 = i0;
  i0 = l18;
  i1 = l19;
  i0 &= i1;
  l20 = i0;
  i0 = l2;
  i1 = l20;
  i32_store((&memory), (u64)(i0 + 28), i1);
  B0:;
  i0 = l2;
  i0 = i32_load((&memory), (u64)(i0 + 28));
  l21 = i0;
  i0 = 32u;
  l22 = i0;
  i0 = l2;
  i1 = l22;
  i0 += i1;
  l23 = i0;
  i0 = l23;
  g0 = i0;
  i0 = l21;
  goto Bfunc;
  Bfunc:;
  FUNC_EPILOGUE;
  return i0;
}

static u32 writev_c(u32 p0, u32 p1, u32 p2) {
  u32 l0 = 0, l1 = 0, l2 = 0, l3 = 0, l4 = 0, l5 = 0, l6 = 0, l7 = 0, 
      l8 = 0, l9 = 0, l10 = 0, l11 = 0, l12 = 0, l13 = 0, l14 = 0, l15 = 0, 
      l16 = 0, l17 = 0, l18 = 0, l19 = 0, l20 = 0, l21 = 0, l22 = 0, l23 = 0, 
      l24 = 0, l25 = 0, l26 = 0, l27 = 0, l28 = 0, l29 = 0, l30 = 0, l31 = 0, 
      l32 = 0, l33 = 0, l34 = 0, l35 = 0, l36 = 0, l37 = 0, l38 = 0, l39 = 0, 
      l40 = 0, l41 = 0, l42 = 0, l43 = 0, l44 = 0, l45 = 0, l46 = 0, l47 = 0, 
      l48 = 0, l49 = 0, l50 = 0;
  FUNC_PROLOGUE;
  u32 i0, i1;
  i0 = g0;
  l0 = i0;
  i0 = 32u;
  l1 = i0;
  i0 = l0;
  i1 = l1;
  i0 -= i1;
  l2 = i0;
  i0 = l2;
  g0 = i0;
  i0 = 0u;
  l3 = i0;
  i0 = l2;
  i1 = p0;
  i32_store((&memory), (u64)(i0 + 28), i1);
  i0 = l2;
  i1 = p1;
  i32_store((&memory), (u64)(i0 + 24), i1);
  i0 = l2;
  i1 = p2;
  i32_store((&memory), (u64)(i0 + 20), i1);
  i0 = l2;
  i1 = l3;
  i32_store((&memory), (u64)(i0 + 16), i1);
  i0 = l2;
  i1 = l3;
  i32_store((&memory), (u64)(i0 + 12), i1);
  L1: 
    i0 = l2;
    i0 = i32_load((&memory), (u64)(i0 + 12));
    l4 = i0;
    i0 = l2;
    i0 = i32_load((&memory), (u64)(i0 + 20));
    l5 = i0;
    i0 = l4;
    l6 = i0;
    i0 = l5;
    l7 = i0;
    i0 = l6;
    i1 = l7;
    i0 = (u32)((s32)i0 < (s32)i1);
    l8 = i0;
    i0 = l8;
    l9 = i0;
    i0 = l9;
    i0 = !(i0);
    if (i0) {goto B0;}
    i0 = 0u;
    l10 = i0;
    i0 = l2;
    i1 = l10;
    i32_store((&memory), (u64)(i0 + 8), i1);
    L3: 
      i0 = l2;
      i0 = i32_load((&memory), (u64)(i0 + 8));
      l11 = i0;
      i0 = l2;
      i0 = i32_load((&memory), (u64)(i0 + 24));
      l12 = i0;
      i0 = l2;
      i0 = i32_load((&memory), (u64)(i0 + 12));
      l13 = i0;
      i0 = 3u;
      l14 = i0;
      i0 = l13;
      i1 = l14;
      i0 <<= (i1 & 31);
      l15 = i0;
      i0 = l12;
      i1 = l15;
      i0 += i1;
      l16 = i0;
      i0 = l16;
      i0 = i32_load((&memory), (u64)(i0 + 4));
      l17 = i0;
      i0 = l11;
      l18 = i0;
      i0 = l17;
      l19 = i0;
      i0 = l18;
      i1 = l19;
      i0 = i0 < i1;
      l20 = i0;
      i0 = l20;
      l21 = i0;
      i0 = l21;
      i0 = !(i0);
      if (i0) {goto B2;}
      i0 = l2;
      i0 = i32_load((&memory), (u64)(i0 + 24));
      l22 = i0;
      i0 = l2;
      i0 = i32_load((&memory), (u64)(i0 + 12));
      l23 = i0;
      i0 = 3u;
      l24 = i0;
      i0 = l23;
      i1 = l24;
      i0 <<= (i1 & 31);
      l25 = i0;
      i0 = l22;
      i1 = l25;
      i0 += i1;
      l26 = i0;
      i0 = l26;
      i0 = i32_load((&memory), (u64)(i0));
      l27 = i0;
      i0 = l2;
      i0 = i32_load((&memory), (u64)(i0 + 8));
      l28 = i0;
      i0 = l27;
      i1 = l28;
      i0 += i1;
      l29 = i0;
      i0 = l29;
      i0 = i32_load8_u((&memory), (u64)(i0));
      l30 = i0;
      i0 = 24u;
      l31 = i0;
      i0 = l30;
      i1 = l31;
      i0 <<= (i1 & 31);
      l32 = i0;
      i0 = l32;
      i1 = l31;
      i0 = (u32)((s32)i0 >> (i1 & 31));
      l33 = i0;
      i0 = l33;
      (*Z_envZ_putc_jsZ_vi)(i0);
      i0 = l2;
      i0 = i32_load((&memory), (u64)(i0 + 8));
      l34 = i0;
      i0 = 1u;
      l35 = i0;
      i0 = l34;
      i1 = l35;
      i0 += i1;
      l36 = i0;
      i0 = l2;
      i1 = l36;
      i32_store((&memory), (u64)(i0 + 8), i1);
      goto L3;
    B2:;
    i0 = l2;
    i0 = i32_load((&memory), (u64)(i0 + 24));
    l37 = i0;
    i0 = l2;
    i0 = i32_load((&memory), (u64)(i0 + 12));
    l38 = i0;
    i0 = 3u;
    l39 = i0;
    i0 = l38;
    i1 = l39;
    i0 <<= (i1 & 31);
    l40 = i0;
    i0 = l37;
    i1 = l40;
    i0 += i1;
    l41 = i0;
    i0 = l41;
    i0 = i32_load((&memory), (u64)(i0 + 4));
    l42 = i0;
    i0 = l2;
    i0 = i32_load((&memory), (u64)(i0 + 16));
    l43 = i0;
    i0 = l43;
    i1 = l42;
    i0 += i1;
    l44 = i0;
    i0 = l2;
    i1 = l44;
    i32_store((&memory), (u64)(i0 + 16), i1);
    i0 = l2;
    i0 = i32_load((&memory), (u64)(i0 + 12));
    l45 = i0;
    i0 = 1u;
    l46 = i0;
    i0 = l45;
    i1 = l46;
    i0 += i1;
    l47 = i0;
    i0 = l2;
    i1 = l47;
    i32_store((&memory), (u64)(i0 + 12), i1);
    goto L1;
  B0:;
  i0 = l2;
  i0 = i32_load((&memory), (u64)(i0 + 16));
  l48 = i0;
  i0 = 32u;
  l49 = i0;
  i0 = l2;
  i1 = l49;
  i0 += i1;
  l50 = i0;
  i0 = l50;
  g0 = i0;
  i0 = l48;
  goto Bfunc;
  Bfunc:;
  FUNC_EPILOGUE;
  return i0;
}

static const u8 data_segment_data_0[] = {
  0x01, 0x00, 0x00, 0x00, 0x02, 0x00, 0x00, 0x00, 0x03, 0x00, 0x00, 0x00, 
  0x04, 0x00, 0x00, 0x00, 0x05, 0x00, 0x00, 0x00, 0x06, 0x00, 0x00, 0x00, 
  0x07, 0x00, 0x00, 0x00, 
};

static void init_memory(void) {
  wasm_rt_allocate_memory((&memory), 2, 65536);
  memcpy(&(memory.data[1024u]), data_segment_data_0, 28);
}

static void init_table(void) {
  uint32_t offset;
  wasm_rt_allocate_table((&T0), 8, 8);
  offset = 1u;
  T0.data[offset + 0] = (wasm_rt_elem_t){func_types[0], (wasm_rt_anyfunc_t)(&f2)};
  T0.data[offset + 1] = (wasm_rt_elem_t){func_types[0], (wasm_rt_anyfunc_t)(&f3)};
  T0.data[offset + 2] = (wasm_rt_elem_t){func_types[0], (wasm_rt_anyfunc_t)(&f4)};
  T0.data[offset + 3] = (wasm_rt_elem_t){func_types[0], (wasm_rt_anyfunc_t)(&f5)};
  T0.data[offset + 4] = (wasm_rt_elem_t){func_types[0], (wasm_rt_anyfunc_t)(&f6)};
  T0.data[offset + 5] = (wasm_rt_elem_t){func_types[0], (wasm_rt_anyfunc_t)(&f7)};
  T0.data[offset + 6] = (wasm_rt_elem_t){func_types[0], (wasm_rt_anyfunc_t)(&f8)};
}

/* export: 'memory' */
wasm_rt_memory_t (*WASM_RT_ADD_PREFIX(Z_memory));
/* export: '__heap_base' */
u32 (*WASM_RT_ADD_PREFIX(Z___heap_baseZ_i));
/* export: '__data_end' */
u32 (*WASM_RT_ADD_PREFIX(Z___data_endZ_i));
/* export: 'Match' */
u32 (*WASM_RT_ADD_PREFIX(Z_MatchZ_iiiii))(u32, u32, u32, u32);
/* export: 'writev_c' */
u32 (*WASM_RT_ADD_PREFIX(Z_writev_cZ_iiii))(u32, u32, u32);

static void init_exports(void) {
  /* export: 'memory' */
  WASM_RT_ADD_PREFIX(Z_memory) = (&memory);
  /* export: '__heap_base' */
  WASM_RT_ADD_PREFIX(Z___heap_baseZ_i) = (&__heap_base);
  /* export: '__data_end' */
  WASM_RT_ADD_PREFIX(Z___data_endZ_i) = (&__data_end);
  /* export: 'Match' */
  WASM_RT_ADD_PREFIX(Z_MatchZ_iiiii) = (&Match);
  /* export: 'writev_c' */
  WASM_RT_ADD_PREFIX(Z_writev_cZ_iiii) = (&writev_c);
}

void WASM_RT_ADD_PREFIX(init)(void) {
  init_func_types();
  init_globals();
  init_memory();
  init_table();
  init_exports();
}
