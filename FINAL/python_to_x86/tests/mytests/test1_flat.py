def lambda_div_0_15_3(fvs_15_2, a_1, b_1):
    tmp_15_30 = inject_int(0)
    tmp_15_31 = fvs_15_2[tmp_15_30]
    lessthan_0 = tmp_15_31
    tmp_15_32 = [lessthan_0]
    tmp_15_33 = create_closure(lambda_div_0_15_3, tmp_15_32)
    tmp_15_34 = inject_big(tmp_15_33)
    tmp_15_35 = [tmp_15_34]
    div_0 = tmp_15_35
    tmp_15_36 = inject_int(0)
    tmp_15_37 = lessthan_0[tmp_15_36]
    tmp_15_38 = get_free_vars(tmp_15_37)
    tmp_15_39 = inject_int(0)
    tmp_15_40 = lessthan_0[tmp_15_39]
    tmp_15_41 = get_fun_ptr(tmp_15_40)
    tmp_15_42 = tmp_15_41(tmp_15_38, a_1, b_1)
    tmp_15_43 = inject_int(0)
    tmp_15_44 = is_true(tmp_15_42)
    if tmp_15_44:
        tmp_15_45 = inject_int(0)
        tmp_15_43 = tmp_15_45
    else:
        tmp_15_46 = inject_int(0)
        tmp_15_47 = div_0[tmp_15_46]
        tmp_15_48 = get_free_vars(tmp_15_47)
        tmp_15_16 = a_1
        tmp_15_49 = -b_1
        tmp_15_50 = inject_int(tmp_15_49)
        tmp_15_17 = tmp_15_50
        tmp_15_51 = is_int(tmp_15_16)
        tmp_15_52 = inject_int(tmp_15_51)
        tmp_15_53 = is_bool(tmp_15_16)
        tmp_15_54 = inject_int(tmp_15_53)
        tmp_15_55 = inject_int(0)
        tmp_15_56 = is_true(tmp_15_52)
        if tmp_15_56:
            tmp_15_55 = tmp_15_52
        else:
            tmp_15_55 = tmp_15_54
        tmp_15_57 = is_int(tmp_15_17)
        tmp_15_58 = inject_int(tmp_15_57)
        tmp_15_59 = is_bool(tmp_15_17)
        tmp_15_60 = inject_int(tmp_15_59)
        tmp_15_61 = inject_int(0)
        tmp_15_62 = is_true(tmp_15_58)
        if tmp_15_62:
            tmp_15_61 = tmp_15_58
        else:
            tmp_15_61 = tmp_15_60
        tmp_15_63 = inject_int(0)
        tmp_15_64 = is_true(tmp_15_55)
        if tmp_15_64:
            tmp_15_63 = tmp_15_61
        else:
            tmp_15_63 = tmp_15_55
        tmp_15_65 = inject_int(0)
        tmp_15_66 = is_true(tmp_15_63)
        if tmp_15_66:
            tmp_15_67 = tmp_15_16 + tmp_15_17
            tmp_15_68 = inject_int(tmp_15_67)
            tmp_15_65 = tmp_15_68
        else:
            tmp_15_69 = is_big(tmp_15_16)
            tmp_15_70 = inject_int(tmp_15_69)
            tmp_15_71 = is_big(tmp_15_17)
            tmp_15_72 = inject_int(tmp_15_71)
            tmp_15_73 = inject_int(0)
            tmp_15_74 = is_true(tmp_15_70)
            if tmp_15_74:
                tmp_15_73 = tmp_15_72
            else:
                tmp_15_73 = tmp_15_70
            tmp_15_75 = inject_int(0)
            tmp_15_76 = is_true(tmp_15_73)
            if tmp_15_76:
                tmp_15_77 = project_big(tmp_15_16)
                tmp_15_78 = project_big(tmp_15_17)
                tmp_15_79 = add(tmp_15_77, tmp_15_78)
                tmp_15_80 = inject_big(tmp_15_79)
                tmp_15_75 = tmp_15_80
            else:
                tmp_15_81 = error_pyobj(0)
                tmp_15_75 = tmp_15_81
            tmp_15_65 = tmp_15_75
        tmp_15_82 = inject_int(0)
        tmp_15_83 = div_0[tmp_15_82]
        tmp_15_84 = get_fun_ptr(tmp_15_83)
        tmp_15_85 = tmp_15_84(tmp_15_48, tmp_15_65, b_1)
        tmp_15_14 = tmp_15_85
        tmp_15_86 = inject_int(1)
        tmp_15_15 = tmp_15_86
        tmp_15_87 = is_int(tmp_15_14)
        tmp_15_88 = inject_int(tmp_15_87)
        tmp_15_89 = is_bool(tmp_15_14)
        tmp_15_90 = inject_int(tmp_15_89)
        tmp_15_91 = inject_int(0)
        tmp_15_92 = is_true(tmp_15_88)
        if tmp_15_92:
            tmp_15_91 = tmp_15_88
        else:
            tmp_15_91 = tmp_15_90
        tmp_15_93 = is_int(tmp_15_15)
        tmp_15_94 = inject_int(tmp_15_93)
        tmp_15_95 = is_bool(tmp_15_15)
        tmp_15_96 = inject_int(tmp_15_95)
        tmp_15_97 = inject_int(0)
        tmp_15_98 = is_true(tmp_15_94)
        if tmp_15_98:
            tmp_15_97 = tmp_15_94
        else:
            tmp_15_97 = tmp_15_96
        tmp_15_99 = inject_int(0)
        tmp_15_100 = is_true(tmp_15_91)
        if tmp_15_100:
            tmp_15_99 = tmp_15_97
        else:
            tmp_15_99 = tmp_15_91
        tmp_15_101 = inject_int(0)
        tmp_15_102 = is_true(tmp_15_99)
        if tmp_15_102:
            tmp_15_103 = tmp_15_14 + tmp_15_15
            tmp_15_104 = inject_int(tmp_15_103)
            tmp_15_101 = tmp_15_104
        else:
            tmp_15_105 = is_big(tmp_15_14)
            tmp_15_106 = inject_int(tmp_15_105)
            tmp_15_107 = is_big(tmp_15_15)
            tmp_15_108 = inject_int(tmp_15_107)
            tmp_15_109 = inject_int(0)
            tmp_15_110 = is_true(tmp_15_106)
            if tmp_15_110:
                tmp_15_109 = tmp_15_108
            else:
                tmp_15_109 = tmp_15_106
            tmp_15_111 = inject_int(0)
            tmp_15_112 = is_true(tmp_15_109)
            if tmp_15_112:
                tmp_15_113 = project_big(tmp_15_14)
                tmp_15_114 = project_big(tmp_15_15)
                tmp_15_115 = add(tmp_15_113, tmp_15_114)
                tmp_15_116 = inject_big(tmp_15_115)
                tmp_15_111 = tmp_15_116
            else:
                tmp_15_117 = error_pyobj(0)
                tmp_15_111 = tmp_15_117
            tmp_15_101 = tmp_15_111
        tmp_15_43 = tmp_15_101
    return tmp_15_43
    

def lambda_lessthan_0_15_5(fvs_15_4, a_1, b_1):
    tmp_15_118 = []
    tmp_15_119 = create_closure(lambda_lessthan_0_15_5, tmp_15_118)
    tmp_15_120 = inject_big(tmp_15_119)
    tmp_15_121 = [tmp_15_120]
    lessthan_0 = tmp_15_121
    tmp_15_122 = inject_int(0)
    tmp_15_123 = a_1 == tmp_15_122
    tmp_15_124 = inject_int(0)
    tmp_15_125 = is_true(tmp_15_123)
    if tmp_15_125:
        tmp_15_126 = inject_bool(1)
        tmp_15_124 = tmp_15_126
    else:
        tmp_15_127 = inject_int(0)
        tmp_15_128 = b_1 == tmp_15_127
        tmp_15_129 = inject_int(0)
        tmp_15_130 = is_true(tmp_15_128)
        if tmp_15_130:
            tmp_15_131 = inject_bool(0)
            tmp_15_129 = tmp_15_131
        else:
            tmp_15_132 = inject_int(0)
            tmp_15_133 = lessthan_0[tmp_15_132]
            tmp_15_134 = get_free_vars(tmp_15_133)
            tmp_15_18 = a_1
            tmp_15_135 = inject_int(1)
            tmp_15_136 = -tmp_15_135
            tmp_15_137 = inject_int(tmp_15_136)
            tmp_15_19 = tmp_15_137
            tmp_15_138 = is_int(tmp_15_18)
            tmp_15_139 = inject_int(tmp_15_138)
            tmp_15_140 = is_bool(tmp_15_18)
            tmp_15_141 = inject_int(tmp_15_140)
            tmp_15_142 = inject_int(0)
            tmp_15_143 = is_true(tmp_15_139)
            if tmp_15_143:
                tmp_15_142 = tmp_15_139
            else:
                tmp_15_142 = tmp_15_141
            tmp_15_144 = is_int(tmp_15_19)
            tmp_15_145 = inject_int(tmp_15_144)
            tmp_15_146 = is_bool(tmp_15_19)
            tmp_15_147 = inject_int(tmp_15_146)
            tmp_15_148 = inject_int(0)
            tmp_15_149 = is_true(tmp_15_145)
            if tmp_15_149:
                tmp_15_148 = tmp_15_145
            else:
                tmp_15_148 = tmp_15_147
            tmp_15_150 = inject_int(0)
            tmp_15_151 = is_true(tmp_15_142)
            if tmp_15_151:
                tmp_15_150 = tmp_15_148
            else:
                tmp_15_150 = tmp_15_142
            tmp_15_152 = inject_int(0)
            tmp_15_153 = is_true(tmp_15_150)
            if tmp_15_153:
                tmp_15_154 = tmp_15_18 + tmp_15_19
                tmp_15_155 = inject_int(tmp_15_154)
                tmp_15_152 = tmp_15_155
            else:
                tmp_15_156 = is_big(tmp_15_18)
                tmp_15_157 = inject_int(tmp_15_156)
                tmp_15_158 = is_big(tmp_15_19)
                tmp_15_159 = inject_int(tmp_15_158)
                tmp_15_160 = inject_int(0)
                tmp_15_161 = is_true(tmp_15_157)
                if tmp_15_161:
                    tmp_15_160 = tmp_15_159
                else:
                    tmp_15_160 = tmp_15_157
                tmp_15_162 = inject_int(0)
                tmp_15_163 = is_true(tmp_15_160)
                if tmp_15_163:
                    tmp_15_164 = project_big(tmp_15_18)
                    tmp_15_165 = project_big(tmp_15_19)
                    tmp_15_166 = add(tmp_15_164, tmp_15_165)
                    tmp_15_167 = inject_big(tmp_15_166)
                    tmp_15_162 = tmp_15_167
                else:
                    tmp_15_168 = error_pyobj(0)
                    tmp_15_162 = tmp_15_168
                tmp_15_152 = tmp_15_162
            tmp_15_20 = b_1
            tmp_15_169 = inject_int(1)
            tmp_15_170 = -tmp_15_169
            tmp_15_171 = inject_int(tmp_15_170)
            tmp_15_21 = tmp_15_171
            tmp_15_172 = is_int(tmp_15_20)
            tmp_15_173 = inject_int(tmp_15_172)
            tmp_15_174 = is_bool(tmp_15_20)
            tmp_15_175 = inject_int(tmp_15_174)
            tmp_15_176 = inject_int(0)
            tmp_15_177 = is_true(tmp_15_173)
            if tmp_15_177:
                tmp_15_176 = tmp_15_173
            else:
                tmp_15_176 = tmp_15_175
            tmp_15_178 = is_int(tmp_15_21)
            tmp_15_179 = inject_int(tmp_15_178)
            tmp_15_180 = is_bool(tmp_15_21)
            tmp_15_181 = inject_int(tmp_15_180)
            tmp_15_182 = inject_int(0)
            tmp_15_183 = is_true(tmp_15_179)
            if tmp_15_183:
                tmp_15_182 = tmp_15_179
            else:
                tmp_15_182 = tmp_15_181
            tmp_15_184 = inject_int(0)
            tmp_15_185 = is_true(tmp_15_176)
            if tmp_15_185:
                tmp_15_184 = tmp_15_182
            else:
                tmp_15_184 = tmp_15_176
            tmp_15_186 = inject_int(0)
            tmp_15_187 = is_true(tmp_15_184)
            if tmp_15_187:
                tmp_15_188 = tmp_15_20 + tmp_15_21
                tmp_15_189 = inject_int(tmp_15_188)
                tmp_15_186 = tmp_15_189
            else:
                tmp_15_190 = is_big(tmp_15_20)
                tmp_15_191 = inject_int(tmp_15_190)
                tmp_15_192 = is_big(tmp_15_21)
                tmp_15_193 = inject_int(tmp_15_192)
                tmp_15_194 = inject_int(0)
                tmp_15_195 = is_true(tmp_15_191)
                if tmp_15_195:
                    tmp_15_194 = tmp_15_193
                else:
                    tmp_15_194 = tmp_15_191
                tmp_15_196 = inject_int(0)
                tmp_15_197 = is_true(tmp_15_194)
                if tmp_15_197:
                    tmp_15_198 = project_big(tmp_15_20)
                    tmp_15_199 = project_big(tmp_15_21)
                    tmp_15_200 = add(tmp_15_198, tmp_15_199)
                    tmp_15_201 = inject_big(tmp_15_200)
                    tmp_15_196 = tmp_15_201
                else:
                    tmp_15_202 = error_pyobj(0)
                    tmp_15_196 = tmp_15_202
                tmp_15_186 = tmp_15_196
            tmp_15_203 = inject_int(0)
            tmp_15_204 = lessthan_0[tmp_15_203]
            tmp_15_205 = get_fun_ptr(tmp_15_204)
            tmp_15_206 = tmp_15_205(tmp_15_134, tmp_15_152, tmp_15_186)
            tmp_15_129 = tmp_15_206
        tmp_15_124 = tmp_15_129
    return tmp_15_124
    

def lambda_mult_0_15_7(fvs_15_6, a_1, b_1):
    tmp_15_207 = []
    tmp_15_208 = create_closure(lambda_mult_0_15_7, tmp_15_207)
    tmp_15_209 = inject_big(tmp_15_208)
    tmp_15_210 = [tmp_15_209]
    mult_0 = tmp_15_210
    tmp_15_211 = inject_int(0)
    tmp_15_212 = b_1 == tmp_15_211
    tmp_15_213 = inject_int(0)
    tmp_15_214 = is_true(tmp_15_212)
    if tmp_15_214:
        tmp_15_215 = inject_int(0)
        tmp_15_213 = tmp_15_215
    else:
        tmp_15_22 = a_1
        tmp_15_216 = inject_int(0)
        tmp_15_217 = mult_0[tmp_15_216]
        tmp_15_218 = get_free_vars(tmp_15_217)
        tmp_15_24 = b_1
        tmp_15_219 = inject_int(1)
        tmp_15_220 = -tmp_15_219
        tmp_15_221 = inject_int(tmp_15_220)
        tmp_15_25 = tmp_15_221
        tmp_15_222 = is_int(tmp_15_24)
        tmp_15_223 = inject_int(tmp_15_222)
        tmp_15_224 = is_bool(tmp_15_24)
        tmp_15_225 = inject_int(tmp_15_224)
        tmp_15_226 = inject_int(0)
        tmp_15_227 = is_true(tmp_15_223)
        if tmp_15_227:
            tmp_15_226 = tmp_15_223
        else:
            tmp_15_226 = tmp_15_225
        tmp_15_228 = is_int(tmp_15_25)
        tmp_15_229 = inject_int(tmp_15_228)
        tmp_15_230 = is_bool(tmp_15_25)
        tmp_15_231 = inject_int(tmp_15_230)
        tmp_15_232 = inject_int(0)
        tmp_15_233 = is_true(tmp_15_229)
        if tmp_15_233:
            tmp_15_232 = tmp_15_229
        else:
            tmp_15_232 = tmp_15_231
        tmp_15_234 = inject_int(0)
        tmp_15_235 = is_true(tmp_15_226)
        if tmp_15_235:
            tmp_15_234 = tmp_15_232
        else:
            tmp_15_234 = tmp_15_226
        tmp_15_236 = inject_int(0)
        tmp_15_237 = is_true(tmp_15_234)
        if tmp_15_237:
            tmp_15_238 = tmp_15_24 + tmp_15_25
            tmp_15_239 = inject_int(tmp_15_238)
            tmp_15_236 = tmp_15_239
        else:
            tmp_15_240 = is_big(tmp_15_24)
            tmp_15_241 = inject_int(tmp_15_240)
            tmp_15_242 = is_big(tmp_15_25)
            tmp_15_243 = inject_int(tmp_15_242)
            tmp_15_244 = inject_int(0)
            tmp_15_245 = is_true(tmp_15_241)
            if tmp_15_245:
                tmp_15_244 = tmp_15_243
            else:
                tmp_15_244 = tmp_15_241
            tmp_15_246 = inject_int(0)
            tmp_15_247 = is_true(tmp_15_244)
            if tmp_15_247:
                tmp_15_248 = project_big(tmp_15_24)
                tmp_15_249 = project_big(tmp_15_25)
                tmp_15_250 = add(tmp_15_248, tmp_15_249)
                tmp_15_251 = inject_big(tmp_15_250)
                tmp_15_246 = tmp_15_251
            else:
                tmp_15_252 = error_pyobj(0)
                tmp_15_246 = tmp_15_252
            tmp_15_236 = tmp_15_246
        tmp_15_253 = inject_int(0)
        tmp_15_254 = mult_0[tmp_15_253]
        tmp_15_255 = get_fun_ptr(tmp_15_254)
        tmp_15_256 = tmp_15_255(tmp_15_218, a_1, tmp_15_236)
        tmp_15_23 = tmp_15_256
        tmp_15_257 = is_int(tmp_15_22)
        tmp_15_258 = inject_int(tmp_15_257)
        tmp_15_259 = is_bool(tmp_15_22)
        tmp_15_260 = inject_int(tmp_15_259)
        tmp_15_261 = inject_int(0)
        tmp_15_262 = is_true(tmp_15_258)
        if tmp_15_262:
            tmp_15_261 = tmp_15_258
        else:
            tmp_15_261 = tmp_15_260
        tmp_15_263 = is_int(tmp_15_23)
        tmp_15_264 = inject_int(tmp_15_263)
        tmp_15_265 = is_bool(tmp_15_23)
        tmp_15_266 = inject_int(tmp_15_265)
        tmp_15_267 = inject_int(0)
        tmp_15_268 = is_true(tmp_15_264)
        if tmp_15_268:
            tmp_15_267 = tmp_15_264
        else:
            tmp_15_267 = tmp_15_266
        tmp_15_269 = inject_int(0)
        tmp_15_270 = is_true(tmp_15_261)
        if tmp_15_270:
            tmp_15_269 = tmp_15_267
        else:
            tmp_15_269 = tmp_15_261
        tmp_15_271 = inject_int(0)
        tmp_15_272 = is_true(tmp_15_269)
        if tmp_15_272:
            tmp_15_273 = tmp_15_22 + tmp_15_23
            tmp_15_274 = inject_int(tmp_15_273)
            tmp_15_271 = tmp_15_274
        else:
            tmp_15_275 = is_big(tmp_15_22)
            tmp_15_276 = inject_int(tmp_15_275)
            tmp_15_277 = is_big(tmp_15_23)
            tmp_15_278 = inject_int(tmp_15_277)
            tmp_15_279 = inject_int(0)
            tmp_15_280 = is_true(tmp_15_276)
            if tmp_15_280:
                tmp_15_279 = tmp_15_278
            else:
                tmp_15_279 = tmp_15_276
            tmp_15_281 = inject_int(0)
            tmp_15_282 = is_true(tmp_15_279)
            if tmp_15_282:
                tmp_15_283 = project_big(tmp_15_22)
                tmp_15_284 = project_big(tmp_15_23)
                tmp_15_285 = add(tmp_15_283, tmp_15_284)
                tmp_15_286 = inject_big(tmp_15_285)
                tmp_15_281 = tmp_15_286
            else:
                tmp_15_287 = error_pyobj(0)
                tmp_15_281 = tmp_15_287
            tmp_15_271 = tmp_15_281
        tmp_15_213 = tmp_15_271
    return tmp_15_213
    

def lambda_15_10(fvs_15_9, n_2):
    tmp_15_288 = inject_int(0)
    tmp_15_289 = fvs_15_9[tmp_15_288]
    prod_0 = tmp_15_289
    tmp_15_290 = inject_int(1)
    tmp_15_291 = fvs_15_9[tmp_15_290]
    div_0 = tmp_15_291
    tmp_15_292 = inject_int(2)
    tmp_15_293 = fvs_15_9[tmp_15_292]
    f_1 = tmp_15_293
    tmp_15_294 = inject_int(0)
    tmp_15_295 = div_0[tmp_15_294]
    tmp_15_296 = get_free_vars(tmp_15_295)
    tmp_15_297 = inject_int(0)
    tmp_15_298 = prod_0[tmp_15_297]
    tmp_15_299 = get_free_vars(tmp_15_298)
    tmp_15_300 = inject_int(0)
    tmp_15_301 = f_1[tmp_15_300]
    tmp_15_302 = get_free_vars(tmp_15_301)
    tmp_15_26 = n_2
    tmp_15_303 = inject_int(1)
    tmp_15_27 = tmp_15_303
    tmp_15_304 = is_int(tmp_15_26)
    tmp_15_305 = inject_int(tmp_15_304)
    tmp_15_306 = is_bool(tmp_15_26)
    tmp_15_307 = inject_int(tmp_15_306)
    tmp_15_308 = inject_int(0)
    tmp_15_309 = is_true(tmp_15_305)
    if tmp_15_309:
        tmp_15_308 = tmp_15_305
    else:
        tmp_15_308 = tmp_15_307
    tmp_15_310 = is_int(tmp_15_27)
    tmp_15_311 = inject_int(tmp_15_310)
    tmp_15_312 = is_bool(tmp_15_27)
    tmp_15_313 = inject_int(tmp_15_312)
    tmp_15_314 = inject_int(0)
    tmp_15_315 = is_true(tmp_15_311)
    if tmp_15_315:
        tmp_15_314 = tmp_15_311
    else:
        tmp_15_314 = tmp_15_313
    tmp_15_316 = inject_int(0)
    tmp_15_317 = is_true(tmp_15_308)
    if tmp_15_317:
        tmp_15_316 = tmp_15_314
    else:
        tmp_15_316 = tmp_15_308
    tmp_15_318 = inject_int(0)
    tmp_15_319 = is_true(tmp_15_316)
    if tmp_15_319:
        tmp_15_320 = tmp_15_26 + tmp_15_27
        tmp_15_321 = inject_int(tmp_15_320)
        tmp_15_318 = tmp_15_321
    else:
        tmp_15_322 = is_big(tmp_15_26)
        tmp_15_323 = inject_int(tmp_15_322)
        tmp_15_324 = is_big(tmp_15_27)
        tmp_15_325 = inject_int(tmp_15_324)
        tmp_15_326 = inject_int(0)
        tmp_15_327 = is_true(tmp_15_323)
        if tmp_15_327:
            tmp_15_326 = tmp_15_325
        else:
            tmp_15_326 = tmp_15_323
        tmp_15_328 = inject_int(0)
        tmp_15_329 = is_true(tmp_15_326)
        if tmp_15_329:
            tmp_15_330 = project_big(tmp_15_26)
            tmp_15_331 = project_big(tmp_15_27)
            tmp_15_332 = add(tmp_15_330, tmp_15_331)
            tmp_15_333 = inject_big(tmp_15_332)
            tmp_15_328 = tmp_15_333
        else:
            tmp_15_334 = error_pyobj(0)
            tmp_15_328 = tmp_15_334
        tmp_15_318 = tmp_15_328
    tmp_15_28 = n_2
    tmp_15_335 = inject_int(2)
    tmp_15_29 = tmp_15_335
    tmp_15_336 = is_int(tmp_15_28)
    tmp_15_337 = inject_int(tmp_15_336)
    tmp_15_338 = is_bool(tmp_15_28)
    tmp_15_339 = inject_int(tmp_15_338)
    tmp_15_340 = inject_int(0)
    tmp_15_341 = is_true(tmp_15_337)
    if tmp_15_341:
        tmp_15_340 = tmp_15_337
    else:
        tmp_15_340 = tmp_15_339
    tmp_15_342 = is_int(tmp_15_29)
    tmp_15_343 = inject_int(tmp_15_342)
    tmp_15_344 = is_bool(tmp_15_29)
    tmp_15_345 = inject_int(tmp_15_344)
    tmp_15_346 = inject_int(0)
    tmp_15_347 = is_true(tmp_15_343)
    if tmp_15_347:
        tmp_15_346 = tmp_15_343
    else:
        tmp_15_346 = tmp_15_345
    tmp_15_348 = inject_int(0)
    tmp_15_349 = is_true(tmp_15_340)
    if tmp_15_349:
        tmp_15_348 = tmp_15_346
    else:
        tmp_15_348 = tmp_15_340
    tmp_15_350 = inject_int(0)
    tmp_15_351 = is_true(tmp_15_348)
    if tmp_15_351:
        tmp_15_352 = tmp_15_28 + tmp_15_29
        tmp_15_353 = inject_int(tmp_15_352)
        tmp_15_350 = tmp_15_353
    else:
        tmp_15_354 = is_big(tmp_15_28)
        tmp_15_355 = inject_int(tmp_15_354)
        tmp_15_356 = is_big(tmp_15_29)
        tmp_15_357 = inject_int(tmp_15_356)
        tmp_15_358 = inject_int(0)
        tmp_15_359 = is_true(tmp_15_355)
        if tmp_15_359:
            tmp_15_358 = tmp_15_357
        else:
            tmp_15_358 = tmp_15_355
        tmp_15_360 = inject_int(0)
        tmp_15_361 = is_true(tmp_15_358)
        if tmp_15_361:
            tmp_15_362 = project_big(tmp_15_28)
            tmp_15_363 = project_big(tmp_15_29)
            tmp_15_364 = add(tmp_15_362, tmp_15_363)
            tmp_15_365 = inject_big(tmp_15_364)
            tmp_15_360 = tmp_15_365
        else:
            tmp_15_366 = error_pyobj(0)
            tmp_15_360 = tmp_15_366
        tmp_15_350 = tmp_15_360
    tmp_15_367 = inject_int(0)
    tmp_15_368 = f_1[tmp_15_367]
    tmp_15_369 = get_fun_ptr(tmp_15_368)
    tmp_15_370 = tmp_15_369(tmp_15_302, tmp_15_318, tmp_15_350)
    tmp_15_371 = inject_int(0)
    tmp_15_372 = prod_0[tmp_15_371]
    tmp_15_373 = get_fun_ptr(tmp_15_372)
    tmp_15_374 = tmp_15_373(tmp_15_299, n_2, tmp_15_370)
    tmp_15_375 = inject_int(6)
    tmp_15_376 = inject_int(0)
    tmp_15_377 = div_0[tmp_15_376]
    tmp_15_378 = get_fun_ptr(tmp_15_377)
    tmp_15_379 = tmp_15_378(tmp_15_296, tmp_15_374, tmp_15_375)
    return tmp_15_379
    

def lambda_triangular_sum_0_15_11(fvs_15_8, f_1):
    tmp_15_380 = inject_int(0)
    tmp_15_381 = fvs_15_8[tmp_15_380]
    prod_0 = tmp_15_381
    tmp_15_382 = inject_int(1)
    tmp_15_383 = fvs_15_8[tmp_15_382]
    div_0 = tmp_15_383
    tmp_15_384 = [prod_0, div_0]
    tmp_15_385 = create_closure(lambda_triangular_sum_0_15_11, tmp_15_384)
    tmp_15_386 = inject_big(tmp_15_385)
    triangular_sum_0 = tmp_15_386
    tmp_15_387 = [f_1]
    f_1 = tmp_15_387
    tmp_15_388 = [prod_0, div_0, f_1]
    tmp_15_389 = create_closure(lambda_15_10, tmp_15_388)
    tmp_15_390 = inject_big(tmp_15_389)
    uflattened_lambda_15_1 = tmp_15_390
    return uflattened_lambda_15_1
    

def lambda_prod_0_15_13(fvs_15_12, y_1):
    tmp_15_391 = inject_int(0)
    tmp_15_392 = fvs_15_12[tmp_15_391]
    mult_0 = tmp_15_392
    tmp_15_393 = [mult_0]
    tmp_15_394 = create_closure(lambda_prod_0_15_13, tmp_15_393)
    tmp_15_395 = inject_big(tmp_15_394)
    tmp_15_396 = [tmp_15_395]
    prod_0 = tmp_15_396
    tmp_15_397 = inject_int(0)
    tmp_15_398 = mult_0[tmp_15_397]
    tmp_15_399 = get_free_vars(tmp_15_398)
    tmp_15_400 = inject_int(0)
    tmp_15_401 = mult_0[tmp_15_400]
    tmp_15_402 = get_fun_ptr(tmp_15_401)
    tmp_15_403 = tmp_15_402(tmp_15_399, y_1, y_1)
    return tmp_15_403
    

def main():
    tmp_15_404 = [prod_0, div_0, f_1]
    tmp_15_405 = create_closure(lambda_15_10, tmp_15_404)
    tmp_15_406 = inject_big(tmp_15_405)
    lambda_15_10 = tmp_15_406
    tmp_15_407 = inject_int(0)
    tmp_15_408 = [tmp_15_407]
    prod_0 = tmp_15_408
    tmp_15_409 = inject_int(0)
    tmp_15_410 = [tmp_15_409]
    div_0 = tmp_15_410
    tmp_15_411 = inject_int(0)
    tmp_15_412 = [tmp_15_411]
    mult_0 = tmp_15_412
    tmp_15_413 = inject_int(0)
    tmp_15_414 = [tmp_15_413]
    f_1 = tmp_15_414
    tmp_15_415 = inject_int(0)
    tmp_15_416 = [tmp_15_415]
    lessthan_0 = tmp_15_416
    tmp_15_417 = inject_int(0)
    tmp_15_418 = div_0[tmp_15_417]
    tmp_15_419 = [lessthan_0]
    tmp_15_420 = create_closure(lambda_div_0_15_3, tmp_15_419)
    tmp_15_421 = inject_big(tmp_15_420)
    tmp_15_422 = inject_int(0)
    tmp_15_418 = tmp_15_421
    div_0[tmp_15_422] = tmp_15_418
    tmp_15_423 = inject_int(0)
    tmp_15_424 = lessthan_0[tmp_15_423]
    tmp_15_425 = []
    tmp_15_426 = create_closure(lambda_lessthan_0_15_5, tmp_15_425)
    tmp_15_427 = inject_big(tmp_15_426)
    tmp_15_428 = inject_int(0)
    tmp_15_424 = tmp_15_427
    lessthan_0[tmp_15_428] = tmp_15_424
    tmp_15_429 = inject_int(0)
    tmp_15_430 = mult_0[tmp_15_429]
    tmp_15_431 = []
    tmp_15_432 = create_closure(lambda_mult_0_15_7, tmp_15_431)
    tmp_15_433 = inject_big(tmp_15_432)
    tmp_15_434 = inject_int(0)
    tmp_15_430 = tmp_15_433
    mult_0[tmp_15_434] = tmp_15_430
    tmp_15_435 = [prod_0, div_0]
    tmp_15_436 = create_closure(lambda_triangular_sum_0_15_11, tmp_15_435)
    tmp_15_437 = inject_big(tmp_15_436)
    triangular_sum_0 = tmp_15_437
    tmp_15_438 = inject_int(0)
    tmp_15_439 = prod_0[tmp_15_438]
    tmp_15_440 = [mult_0]
    tmp_15_441 = create_closure(lambda_prod_0_15_13, tmp_15_440)
    tmp_15_442 = inject_big(tmp_15_441)
    tmp_15_443 = inject_int(0)
    tmp_15_439 = tmp_15_442
    prod_0[tmp_15_443] = tmp_15_439
    tmp_15_444 = get_free_vars(triangular_sum_0)
    tmp_15_445 = inject_int(0)
    tmp_15_446 = prod_0[tmp_15_445]
    tmp_15_447 = get_fun_ptr(triangular_sum_0)
    tmp_15_448 = tmp_15_447(tmp_15_444, tmp_15_446)
    sum_func_0 = tmp_15_448
    tmp_15_449 = get_free_vars(sum_func_0)
    tmp_15_450 = inject_int(10)
    tmp_15_451 = get_fun_ptr(sum_func_0)
    tmp_15_452 = tmp_15_451(tmp_15_449, tmp_15_450)
    print(tmp_15_452)

